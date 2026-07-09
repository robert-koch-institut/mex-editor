import { inject } from "@angular/core";
import { Router, type RouterStateSnapshot, type CanActivateFn, type ActivatedRouteSnapshot } from "@angular/router";
import { AuthService } from "./auth";

export const authGuard: CanActivateFn = (
    _route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
) => {
  const authService = inject(AuthService);
  if (authService.isLoggedIn()) {
    return true;
  }

  const router = inject(Router);
  return router.createUrlTree(["/search"], {
    queryParams: { 'loginRequired': "1", 'redirectURL': state.url },
  });
};
