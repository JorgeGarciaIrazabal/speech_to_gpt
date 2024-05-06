import {Component, CUSTOM_ELEMENTS_SCHEMA, OnInit, ViewChild} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {
  IonButton,
  IonButtons, IonCol,
  IonContent, IonFooter, IonGrid,
  IonHeader, IonIcon, IonItem, IonLabel, IonList,
  IonMenuButton, IonRow, IonSpinner,
  IonTitle,
  IonToolbar,
  IonInput
} from '@ionic/angular/standalone';
import {ChatMessage, DefaultService, OpenAPI} from "../../stgpt_api";
import {addIcons} from "ionicons";
import { send } from 'ionicons/icons';
import {MarkdownComponent} from "ngx-markdown";
import { Storage } from '@ionic/storage-angular';
import { Router } from '@angular/router'; // Import Router

@Component({
  selector: 'app-chat',
  templateUrl: './chat.page.html',
  styleUrls: ['./chat.page.scss'],
  standalone: true,
  imports: [IonContent, IonHeader, IonTitle, IonToolbar, CommonModule, FormsModule, IonButtons, IonMenuButton, IonButton, IonList, IonItem, IonLabel, IonFooter, IonInput, IonSpinner, IonIcon, IonRow, IonGrid, IonCol, MarkdownComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ChatPage implements OnInit{
  messages: ChatMessage[] = [];
  newMessage: string = "";
  sendingMessage: boolean = false;
  logMessage: string = "";
  private _storage: Storage | null = null;
  @ViewChild('input') inputElement!: IonInput;

  constructor(private storage: Storage, private router: Router) {
    addIcons({send})
  }

  async ngOnInit() {
    console.log('init ChatPage')
    this._storage = await this.storage.create();

    try {
      const token = await this._storage?.get("token");
      OpenAPI.TOKEN = token.access_token;
      await DefaultService.readUsersMeUsersMeGet()
    } catch (error) {
      console.error('User is not authenticated')
      this.router.navigate(['/login/logout'])
    }
    console.log('User is authenticated')
    setTimeout(() => {
      this.inputElement.setFocus()
    }, 1);
  }

  async sendMessage() {
    await this.storage.create();
    this.messages.push({content:this.newMessage, role: 'user'});
    this.sendingMessage = true;
    let message_text = ""
    try {
      const response = await fetch(OpenAPI.BASE + '/chat', {
        method: 'POST',
        body: JSON.stringify(this.messages),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OpenAPI.TOKEN}`
        }
      });

      if (!response.ok && response.status === 401) {
          // If the status code is 401 (unauthorized), navigate the user back to the 'login/logout' route
          await this.router.navigate(['/login/logout']);
          return;
      }

      const assistantMessage = {content:"", role: 'assistant'};
      this.messages.push(assistantMessage);
      if (response.body == null) {
        throw new Error('Response body is null');
      }
      const reader = response.body.getReader();

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        message_text += new TextDecoder("utf-8").decode(value)
        const splitMessages = message_text.split("%%%%");

        for (let i = 0; i < splitMessages.length - 1; i++) {
          const message = JSON.parse(splitMessages[i]);
          if (message.role === "log_message") {
            this.logMessage = message.content;
            continue;
          }
          assistantMessage.content += message.content;
        }

        message_text = splitMessages[splitMessages.length - 1];
      }
    } catch (error) {
      this.messages.pop();
      console.error(error);
    } finally {
      this.sendingMessage = false;
      this.newMessage = "";
      await this.inputElement.setFocus()
      this.logMessage = "";
    }
  }

  clearChat() {
    this.messages = [];
  }
}
