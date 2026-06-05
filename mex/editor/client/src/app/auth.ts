import { Injectable } from "@angular/core";
import { signal } from "@angular/core";

@Injectable({
  providedIn: "root",
})
export class AuthService {
  isLoggedIn = signal(false);
  username = signal("");

  login(username: string): void {
    this.username.set(username);
    this.isLoggedIn.set(true);
  }

  logout(): void {
    this.username.set("");
    this.isLoggedIn.set(false);
  }
}
