import { secrets } from 'src/secrets';

export const environment = {
  production: false,
  apiBaseUrl: secrets.urls.api.dev,
};
