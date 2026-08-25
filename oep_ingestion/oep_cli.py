import json

import click

import oep_ingestion
from oep_ingestion.oep_download.get_meta import get_table_metadata, get_table_names

log = oep_ingestion.get_logger("graphon_ingestion.cli")

# =============================================================================
# Main CLI Group
# =============================================================================

@click.group()
@click.version_option(version=oep_ingestion.__version__)
def oep_cli():
    """GraphON Data Ingestion CLI - Manage data ingestion from OEP and other sources."""
    # Configure logging once at entry point
    oep_ingestion.setup_logging("graphon_ingestion")


# =============================================================================
# Info Commands - Database inspection and health checks
# =============================================================================

@oep_cli.group()
def info():
    """Inspect database state and connectivity."""
    pass


@info.command()
def neo():
    """Verify Neo4j connectivity."""
    from neo4j import GraphDatabase

    from config.neo_config import PASSWORD, URI, USER
    
    log.info("Verifying Neo4j connection...")
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        oep_ingestion.neo_ingest_oep.verify_neo4j_connection(driver)
        click.echo("✓ Neo4j connection successful")
    except Exception as e:
        click.echo(f"✗ Neo4j connection failed: {e}", err=True)
        raise SystemExit(1)
    finally:
        driver.close()


@info.command()
@click.option('--schema', '-s', default=None, help='Schema name (default: from config)')
@click.option('--format', '-f', 'fmt', default='list', type=click.Choice(['list', 'json']), help='Output format')
def tables(schema, fmt):
    """List all table names from OEP."""
    try:
        if fmt == 'list':
            table_list = get_table_names(schema=schema, as_list=True)
            click.echo(f"Found {len(table_list)} tables:")
            for table in sorted(table_list):
                click.echo(f"  - {table}")
        else:
            response = get_table_names(schema=schema, as_list=False)
            click.echo(json.dumps(response, indent=2))
    except Exception as e:
        click.echo(f"Error fetching table names: {e}", err=True)
        raise SystemExit(1)


@info.command()
def counts():
    """Show record counts for all tables."""
    log.info("Fetching table counts...")
    counts = oep_ingestion.neo_ingest_oep.get_table_counts()
    click.echo("Table record counts:")
    for table, count in sorted(counts.items()):
        click.echo(f"  {table}: {count:,}")
    total = sum(counts.values())
    click.echo(f"\nTotal records: {total:,}")


@info.command()
def status():
    """Show overall system status."""
    from neo4j import GraphDatabase
    from config.neo_config import PASSWORD, URI, USER
    
    click.echo("System Status:")
    
    # Check Neo4j connectivity
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        oep_ingestion.neo_ingest_oep.verify_neo4j_connection(driver)
        click.echo("  Neo4j: ✓ Connected")
    except Exception as e:
        click.echo(f"  Neo4j: ✗ Disconnected ({e})")
    
    # Show table counts
    try:
        counts = oep_ingestion.neo_ingest_oep.get_table_counts()
        total = sum(counts.values())
        click.echo(f"  Total records: {total:,}")
        click.echo(f"  Tables: {len(counts)}")
    except Exception as e:
        click.echo(f"  Error fetching counts: {e}", err=True)


# =============================================================================
# Data Commands - Fetch, restore, preprocess data from sources
# =============================================================================

@oep_cli.group()
def data():
    """Fetch and manage raw data from sources."""
    pass


@data.command()
@click.option('--source', '-s', default='oep', type=click.Choice(['oep']), help='Data source')
@click.option('--tables', '-t', multiple=True, help='Specific tables to fetch (default: all)')
@click.option('--output', '-o', type=click.Path(), help='Output directory for fetched data (default: RAW_METADATA_DIR from config)')
@click.option('--schema', '-S', default=None, help='OEP schema name (default: from config)')
@click.option('--max-tables', '-m', type=int, default=None, help='Maximum number of tables to fetch (default: unlimited)')
def fetch(source, tables, output, schema, max_tables):
    """Fetch data from a source (e.g., OEP)."""
    import json
    from pathlib import Path
    from config.oep_config import RAW_METADATA_DIR
    
    log.info(f"Fetching data from {source}...")
    if source == 'oep':
        # Use flexible get_table_names for table discovery if no specific tables requested
        table_list = list(tables) if tables else None
        
        if table_list is None:
            try:
                table_list = get_table_names(schema=schema, as_list=True)
                log.info(f"Discovered {len(table_list)} tables from OEP")
            except Exception as e:
                click.echo(f"Error discovering tables: {e}", err=True)
                raise SystemExit(1)
        
        # Standardized fetch interface with timeout handling
        fetched = oep_ingestion.neo_ingest_oep.fetch_from_oep(
            tables=table_list,
            schema=schema,
            max_tables=max_tables
        )
        click.echo(f"Fetched {len(fetched)} of {len(table_list)} tables from OEP")
        
        # Save to output directory (or default RAW_METADATA_DIR)
        save_dir = Path(output) if output else RAW_METADATA_DIR
        save_dir.mkdir(parents=True, exist_ok=True)
        
        for table_name, metadata in fetched.items():
            out_file = save_dir / f"{table_name}_metadata.json"
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        click.echo(f"Data saved to: {save_dir}")
    else:
        click.echo(f"Unsupported source: {source}", err=True)
        raise SystemExit(1)


@data.command()
@click.option('--source', '-s', default='oep', type=click.Choice(['oep']), help='Data source')
@click.option('--path', '-p', required=True, type=click.Path(exists=True), help='Path to previously exported data')
def restore(source, path):
    """Restore data from a previous export."""
    log.info(f"Restoring data from {path}...")
    if source == 'oep':
        restored = oep_ingestion.neo_ingest_oep.restore_from_oep(path)
        click.echo(f"Restored {restored} records from {path}")
    else:
        click.echo(f"Unsupported source: {source}", err=True)
        raise SystemExit(1)


@data.command()
@click.option('--table', '-t', required=True, help='Table name to fetch metadata for')
@click.option('--schema', '-s', default=None, help='Schema name (default: from config)')
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: stdout)')
@click.option('--via-client', is_flag=True, default=True, help='Use OepClient (default) vs direct API')
def metadata(table, schema, output, via_client):
    """Fetch metadata for a specific OEP table."""
    try:
        meta = get_table_metadata(
            table_name=table,
            schema=schema,
            via_client=via_client
        )
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            click.echo(f"Metadata saved to: {output}")
        else:
            click.echo(json.dumps(meta, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error fetching metadata: {e}", err=True)
        raise SystemExit(1)


@data.command()
@click.option('--source', '-s', default='oep', type=click.Choice(['oep']), help='Data source')
@click.option('--tables', '-t', multiple=True, help='Specific tables to preprocess')
@click.option('--input-dir', '-i', type=click.Path(exists=True), help='Directory containing fetched metadata files (default: RAW_METADATA_DIR from config)')
@click.option('--output-dir', '-o', type=click.Path(), help='Directory to save preprocessed files (default: METADATA_DIR from config)')
def preprocess(source, tables, input_dir, output_dir):
    """Preprocess fetched data before ingestion."""
    from pathlib import Path
    from config.oep_config import MODELS_DIR, RAW_METADATA_DIR, METADATA_DIR
    from oep_ingestion.oep_preprocessing.preprocess_data import process_folder
    
    log.info(f"Preprocessing data from {source}...")
    if source == 'oep':
        # Use defaults if not provided
        in_dir = Path(input_dir) if input_dir else RAW_METADATA_DIR
        out_dir = Path(output_dir) if output_dir else METADATA_DIR
        schema_path = MODELS_DIR / "data-model-oep.yaml"
        
        result = process_folder(
            schema_file=str(schema_path),
            input_dir=in_dir,
            output_dir=out_dir,
            tables=list(tables) if tables else None
        )
        click.echo(f"Preprocessed {result['processed']} tables")
    else:
        click.echo(f"Unsupported source: {source}", err=True)
        raise SystemExit(1)


# =============================================================================
# Graph Commands - Merge data into graph and manage graph state
# =============================================================================

@oep_cli.group()
def graph():
    """Manage graph structure and data merging."""
    pass


@graph.command()
@click.option('--source', '-s', default='oep', type=click.Choice(['oep']), help='Data source')
@click.option('--tables', '-t', multiple=True, help='Specific tables to merge')
@click.option('--dry-run', is_flag=True, help='Show what would be merged without applying')
@click.option('--max-tables', '-m', type=int, default=None, help='Maximum number of tables to merge (default: unlimited)')
def merge(source, tables, dry_run, max_tables):
    """Merge data from a source into the graph."""
    log.info(f"Merging data from {source} into graph...")
    if source == 'oep':
        if dry_run:
            click.echo("[DRY RUN] Would merge data from OEP")
            # Could show preview of changes
        else:
            merged = oep_ingestion.neo_ingest_oep.merge_oep_into_graph(
                tables=list(tables) if tables else None,
                max_tables=max_tables
            )
            click.echo(f"Merged {merged} records into graph")
    else:
        click.echo(f"Unsupported source: {source}", err=True)
        raise SystemExit(1)


@graph.command()
@click.option('--backup-path', '-b', type=click.Path(), help='Path to save graph backup')
def backup(backup_path):
    """Create a backup of the current graph state."""
    log.info("Creating graph backup...")
    path = oep_ingestion.neo_ingest_oep.backup_graph(backup_path)
    click.echo(f"Graph backed up to: {path}")


@graph.command()
@click.option('--path', '-p', required=True, type=click.Path(exists=True), help='Path to graph backup')
def restore(path):
    """Restore graph from a backup."""
    log.info(f"Restoring graph from {path}...")
    restored = oep_ingestion.neo_ingest_oep.restore_graph(path)
    click.echo(f"Graph restored from {path}")


@graph.command()
def clear():
    """Clear all data from the graph database."""
    if not click.confirm("This will delete ALL data from the graph. Continue?"):
        click.echo("Aborted.")
        raise SystemExit(0)
    
    log.info("Clearing graph database...")
    oep_ingestion.neo_ingest_oep.clear_database()
    click.echo("Graph database cleared.")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == '__main__':
    oep_cli()