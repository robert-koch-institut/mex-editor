import { secrets } from 'src/secrets';

export const environment = {
  prodMode: true,
  apiBaseUrl: secrets.urls.api.stage,
};
