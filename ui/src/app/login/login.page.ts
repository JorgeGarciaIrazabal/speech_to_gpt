import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonButton,
  IonContent,
  IonHeader,
  IonInput,
  IonItem,
  IonLabel,
  IonTitle,
  IonToolbar
} from '@ionic/angular/standalone';
import { NgForm } from '@angular/forms';
import { Storage } from '@ionic/storage-angular';
import {DefaultService, OpenAPI} from "../../stgpt_api";
import {ActivatedRoute, Router} from '@angular/router'; // Import Router


@Component({
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
  standalone: true,
  imports: [IonContent, IonHeader, IonTitle, IonToolbar, CommonModule, FormsModule, IonItem, IonLabel, IonInput, IonButton]
})
export class LoginPage implements OnInit {
  private _storage: Storage | null = null;

  constructor(private storage: Storage, private router: Router, private route: ActivatedRoute) { }

  async ngOnInit() {
    this._storage = await this.storage.create();
    if (this.route.snapshot.url.toString().includes('logout')) {
      await this.logout();
    }
    if (await this._storage.get("token")) {
      console.log("Token found");
      this.router.navigate(['/chat']);
    }
  }

  async logout() {
    await this._storage?.remove("token");
  }

  async onSubmit(form: NgForm) {
    try {
      let token = await DefaultService.loginForAccessTokenTokenPost({
        username: form.value.email,
        password: form.value.password
      })
      await this._storage?.set("token", token);
      OpenAPI.TOKEN = token.access_token;
      this.router.navigate(['/chat']);
    } catch (e) {
      console.error(e);
    } finally {
    }
  }
}
