import { provideHttpClient } from "@angular/common/http";
import { provideHttpClientTesting } from "@angular/common/http/testing";
import { provideRouter } from "@angular/router";

const testProviders = [provideRouter([]), provideHttpClient(), provideHttpClientTesting()];

export default testProviders;
