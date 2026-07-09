import { inject } from "@angular/core";
import { Router, type CanActivateFn } from "@angular/router";
import { AuthService } from "./auth";

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  if (authService.isLoggedIn()) {
    return true;
  }

  const router = inject(Router);
  return router.createUrlTree(["/search"], {
    queryParams: { loginRequired: "1" },
  });
};
