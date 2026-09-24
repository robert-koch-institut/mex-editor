import { Component } from "@angular/core";
import { MatButtonModule } from "@angular/material/button";
import { MatIcon } from "@angular/material/icon";
import { TranslocoDirective } from "@jsverse/transloco";

@Component({
  selector: "mex-user-logout",
  imports: [MatButtonModule, MatIcon, TranslocoDirective],
  templateUrl: "./user-logout.html",
  styleUrl: "./user-logout.scss",
})
/**
 * Component to allow to user to logout.
 */
export class UserLogout {
  loggedInUser = { name: "rkid1\\NachnameV" };

  logout() {
    window.alert("Logging out..");
  }
}
