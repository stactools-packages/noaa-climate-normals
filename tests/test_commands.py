import os.path
from tempfile import TemporaryDirectory

import pystac
from stactools.testing import CliTestCase

from stactools.noaa_climate_normals.commands import \
    create_noaa_climate_normals_command

from . import test_data


class CommandsTest(CliTestCase):

    def create_subcommand_functions(self):
        return [create_noaa_climate_normals_command]

    def test_create_collection(self):
        source = test_data.get_path("data-files/normals-monthly")
        with TemporaryDirectory() as tmp_dir:
            destination = os.path.join(tmp_dir, "output")
            result = self.run_command([
                "noaa-climate-normals", "create-collection", source,
                destination
            ])

            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            collection = pystac.read_file(destination)
            self.assertEqual(collection.id, "my-collection-id")
            # self.assertEqual(item.other_attr...

            collection.validate()

    def test_create_item(self):
        with TemporaryDirectory() as tmp_dir:
            # Run your custom create-item command and validate

            # Example:
            destination = os.path.join(tmp_dir, "item.json")
            result = self.run_command([
                "noaa-climate-normals",
                "create-item",
                "/path/to/asset.tif",
                destination,
            ])
            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item = pystac.read_file(destination)
            self.assertEqual(item.id, "my-item-id")
            # self.assertEqual(item.other_attr...

            item.validate()
