import { inject } from "@angular/core";
import { MatDialog } from "@angular/material/dialog";
import { Router, type RouterStateSnapshot, type CanActivateFn, type ActivatedRouteSnapshot } from "@angular/router";
import { firstValueFrom } from "rxjs";
import { AuthService } from "./auth";
import { LoginDialogComponent } from "./app";

// login now completely handled by route guard.
// user tries to open protected route -> guard checks if logged in
// if not, guard opens the login dialog and waits for result.
// app.ts still has its own login button with same DialogComponent.

export const authGuard: CanActivateFn = async (
    _route: ActivatedRouteSnapshot,
  _state: RouterStateSnapshot
) => {
  // Check if the user is already logged in
  const authService = inject(AuthService);
  if (authService.isLoggedIn()) {
    return true;
  }
  // else open login dialog and wait for result
  const loginDialog = inject(MatDialog);
  const router = inject(Router);
  const dialogReference = loginDialog.open(LoginDialogComponent); // observe when dialog is closed and get result
  //  dialogReference.afterClosed() returns an observable that emits the result when the dialog is closed
  // use firstValueFrom to convert it to a promise (await single emission instead of subscribing)
  const result = await firstValueFrom(dialogReference.afterClosed());

  if (result?.success) {
    authService.login(result.username);
    return true;
  }

  return router.createUrlTree(["/search"]);
};
