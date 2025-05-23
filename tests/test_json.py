#!/usr/bin/env python3

import os, unittest, json, warnings

schemapath = os.path.join(os.path.dirname(__file__), '..', 'source', 'langtags_schema.json')
testfile = os.path.join(os.path.dirname(__file__), '..', 'pub', 'langtags.json')


class JsonSchemaTest(unittest.TestCase):
    ''' Tests that generated JSON conforms to the schema '''
    def test_jsonschema(self):
        try:
            from jsonschema.validators import validator_for
        except ImportError:
            self.skipTest("Python jsonschema module is missing")

        with open(schemapath) as inf:
            schema = json.load(inf)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            factory = validator_for(schema)
        validator = factory(schema=schema)
        validator.check_schema(schema)
        errors = []
        with open(testfile) as inf:
            testdata = json.load(inf)
        for error in validator.iter_errors(testdata):
            errors.append(error.message)
        if len(errors) > 0:
            self.fail("\n".join(errors))


if __name__ == '__main__':
    unittest.main()
