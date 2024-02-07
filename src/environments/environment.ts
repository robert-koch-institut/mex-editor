import { secrets } from 'src/secrets';

export const environment = {
  prodMode: false,
  apiBaseUrl: secrets.urls.api.dev,
};
