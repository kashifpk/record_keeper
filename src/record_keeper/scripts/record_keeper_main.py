"""Main record_keeper command."""

from datetime import datetime

import click
import transaction

from .. import init  # pylint: disable=E0402
from ..app_objects import app  # pylint: disable=E0402
from .. import models  # noqa


@click.group()
def cli():
    """Group for record keeper commands."""
    init()


@cli.command()
def initdb():
    """Create db and tables."""
    app.DBBase.metadata.create_all(app.db.get_bind())
    click.secho("[DB] - Tables created.")


@cli.command()
@click.argument("catalog")
@click.argument("volume_label")
@click.argument("entries", nargs=-1, type=click.Path(exists=True))
def add(catalog, volume_label, entries):  # noqa
    """
    Add a new catalog.

    \b
    Examples
        record_keeper add TV supernatural_s15 /E/TV/Supernatural/*
        record_keeper add M movies "avengers" "avengers-civil-war" "avengers-3"
        record_keeper DOCS DOCS-01 Intro.docs /MyDocuments/*
    """

    c_type = ""
    c_id = None

    if "-" in catalog:
        # XF-1090
        parts = catalog.split("-")
        c_type = parts[0]
        c_id = int(parts[1])

    else:  # fetch latest catalog_id from db for given catalog type
        c_type = catalog
        catalog_rec = (
            app.db.query(models.Catalog)
            .filter_by(catalog_type=c_type)
            .order_by(models.Catalog.catalog_number.desc())
            .first()
        )
        if catalog_rec:
            c_id = int(catalog_rec.catalog_number) + 1
        else:
            c_id = 1

    assert c_type and c_id

    with transaction.manager:
        new_catalog = models.Catalog(
            catalog_id=f"{c_type}-{c_id}",
            catalog_type=c_type,
            catalog_number=c_id,
            volume_label=volume_label,
            timestamp=datetime.now(),
        )

        app.db.add(new_catalog)
        app.db.flush()

        for fl in entries:
            app.db.add(
                models.Listing(catalog_id=new_catalog.catalog_id, path=fl)
            )

        app.db.flush()

    click.secho(
        f" - Created {new_catalog.catalog_id} with {len(entries)} files.",
        bold=True,
        fg="green",
    )


@cli.command()
@click.argument("catalog")
def list(catalog):  # noqa
    """
    List catalogs of a category or list contents of a catalog.

    \b
    Examples
        List all catalogs of a category

            record_keeper list TV

        List contents of a specific catalog.

            record_keeper list XF-1090
    """
    if "-" in catalog:  # list catalog contents
        # XF-1090
        q = app.db.query(models.Listing).filter_by(catalog_id=catalog)
        click.secho(f"Showing contents of catalog: {catalog}", bold=True)
        click.secho("-" * 75, bold=True)

        for r in q:
            click.secho(r.path)

    else:  # List catalogs of category
        q = app.db.query(models.Catalog).filter_by(catalog_type=catalog)
        click.secho(
            "Catalog ID".ljust(25, " ")
            + "Volume Label".ljust(40, " ")
            + "Timestamp".ljust(10, " "),
            bold=True,
        )
        click.secho("-" * 75, bold=True)

        for r in q:
            click.secho(
                r.catalog_id.ljust(25, " ")
                + r.volume_label.ljust(40, " ")
                + r.timestamp.date().isoformat().ljust(10, " ")
            )
