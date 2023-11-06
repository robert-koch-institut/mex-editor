import { secrets } from 'src/secrets';

export const environment = {
  production: true,
  apiBaseUrl: secrets.urls.api.prod,
};
