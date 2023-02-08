#!/usr/bin/python3

import os, unittest, json

try:
    import jsonschema
except ModuleError:
    jsonschema = None

schemapath = os.path.join(os.path.dirname(__file__), '..', 'source', 'langtags_schema.json')
testfile = os.path.join(os.path.dirname(__file__), '..', 'pub', 'langtags.json')
error_format = "{error.message}"

class JsonSchemaTest(unittest.TestCase):
    ''' Tests that generated JSON conforms to the schema '''
    def setup(self):
        if jsonschema is None:
            self.skipTest("Python jsonschema module is missing")

    def test_jsonschema(self):
        with open(schemapath) as inf:
            schema = json.load(inf)
        factory = jsonschema.validators.validator_for(schema)
        validator = factory(schema=schema)
        validator.check_schema(schema)
        errors = []
        with open(testfile) as inf:
            testdata = json.load(inf)
        for error in validator.iter_errors(testdata):
            errors.append(error_format.format(error=error))
        if len(errors):
            self.fail("\n".join(errors))


if __name__ == '__main__':
    unittest.main()
