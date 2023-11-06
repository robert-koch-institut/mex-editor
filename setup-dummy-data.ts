import * as _ from 'lodash-es';
import { JsonSchemaNormalizer } from './src/app/models/json-schema-normalizer';
import { readJSONSync, } from 'fs-extra';
import { JSONSchemaFaker } from 'json-schema-faker';
import { join } from 'path';
import { glob } from 'glob';
import { writeFile } from 'fs/promises';

const schemaSourceDir = '/src/assets/schema';
const dataTargetDir = '/src/assets/data';
const entitesSchemaDir = '/entities';

(async function run() {
  const cwd = join(__dirname, schemaSourceDir, entitesSchemaDir);
  const entitySchemas = await glob(['*.json'], { cwd, ignore: ['*.genfix.json'] });
  console.log("Generating dummy data for", entitySchemas);
  const parser = new JsonSchemaNormalizer();

  const normalizedSchemas = entitySchemas.map(x => {
    const schema = readJSONSync(join(cwd, x), { encoding: 'utf8' });
    const normalizedSchema = parser.normalize(schema, schema);
    return { filename: x, schema: normalizedSchema };
  });

  const dummyData = normalizedSchemas.reduce((prev, curr) => {
    const schemaAsString = JSON.stringify(curr.schema);
    const noUuid4 = schemaAsString.replace(/"uuid4"/g, "\"uuid\"");
    try {
      const fake = JSONSchemaFaker.generate(JSON.parse(noUuid4));
      const fake1 = JSONSchemaFaker.generate(JSON.parse(noUuid4));
      const fake2 = JSONSchemaFaker.generate(JSON.parse(noUuid4));
      prev[curr.filename] = [fake, fake1, fake2];
    } catch (err) {
      console.error(`Error while generating dummy data for '${curr.filename}'.`, err);
    }
    return prev;
  }, {} as Record<string, unknown[]>);

  await Promise.all(_.map(dummyData, async (x, k) => {
    const filepath = join(__dirname, dataTargetDir, k);
    await writeFile(filepath, JSON.stringify(x, undefined, 2), { encoding: 'utf8' });
    console.log(`  - Successfully wrote file ${filepath}.`);
  }));
  console.log("Dummy data successfully generated.");
})();
