import { MatButtonModule } from "@angular/material/button";
import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { MatDialog } from "@angular/material/dialog";
import { MatDialogModule } from "@angular/material/dialog";
import { MatDialogRef } from "@angular/material/dialog";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatSnackBar, MatSnackBarModule } from "@angular/material/snack-bar";
import { RouterLink, RouterLinkActive, RouterOutlet } from "@angular/router";
import { AuthService } from "./auth";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [
    FormsModule,
    MatDialogModule,
    MatSnackBarModule,
    RouterLink,
    RouterLinkActive,
    RouterOutlet,
  ],
  templateUrl: "./app.html",
  styleUrl: "./app.scss",
})
export class App {
  protected readonly title = signal("mex-editor-ng");
  private loginDialog = inject(MatDialog);
  private loginSnackBar = inject(MatSnackBar);
  private authService = inject(AuthService);

  credentials = {
    username: "",
  };

  get isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }

  openLogin(): void {
    const dialogRef = this.loginDialog.open(LoginDialogComponent);

    dialogRef.afterClosed().subscribe((result) => {
      if (result?.success) {
        this.credentials.username = result.username;
        this.authService.login(result.username);
        this.loginSnackBar.open(`Successfully logged in as ${result.username}.`, "Close", { duration: 3000 });
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.credentials.username = "";
  }

}

@Component({
  selector: "app-login-dialog",
  standalone: true,
  imports: [
    FormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  template: `
    <h2 mat-dialog-title>Login</h2>
    <div mat-dialog-content style="padding-top: 25px;">
      <mat-form-field appearance="outline" style="width: 100%;">
        <mat-label>Username</mat-label>
        <input matInput [(ngModel)]="username" name="username" />
      </mat-form-field>

      <mat-form-field appearance="outline" style="width: 100%;">
        <mat-label>Password</mat-label>
        <input matInput [(ngModel)]="password" name="password" type="password" />
      </mat-form-field>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button type="button" (click)="close()">Cancel</button>
      <button mat-flat-button color="primary" type="button" (click)="login()">Login</button>
    </div>
  `,
})
export class LoginDialogComponent {
  private dialogRef = inject(MatDialogRef<LoginDialogComponent>);

  username = "";
  password = "";

  login(): void {
    this.dialogRef.close({
      success: true,
      username: this.username,
    });
  }

  close(): void {
    this.dialogRef.close({
      success: false
    });
  }
}
