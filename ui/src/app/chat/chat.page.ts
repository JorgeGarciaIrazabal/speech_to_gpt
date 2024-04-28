import {Component, OnInit, ViewChild} from '@angular/core';
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


@Component({
  selector: 'app-chat',
  templateUrl: './chat.page.html',
  styleUrls: ['./chat.page.scss'],
  standalone: true,
  imports: [IonContent, IonHeader, IonTitle, IonToolbar, CommonModule, FormsModule, IonButtons, IonMenuButton, IonButton, IonList, IonItem, IonLabel, IonFooter, IonInput, IonSpinner, IonIcon, IonRow, IonGrid, IonCol]
})
export class ChatPage implements OnInit{
  messages: ChatMessage[] = [];
  newMessage: string = "";
  sendingMessage: boolean = false;
  @ViewChild('input') inputElement!: IonInput;

  constructor() {
    addIcons({send})
  }

  ngOnInit() {
    console.log('init ChatPage')
    setTimeout(() => {
      this.inputElement.setFocus()
    }, 1);
  }

  async sendMessage() {
    OpenAPI.BASE = 'http://0.0.0.0:8181';
    this.messages.push({content:this.newMessage, role: 'user'});
    this.sendingMessage = true;
    try {
      let response = await DefaultService.chatEndpointChatPost(this.messages);
      this.messages.push({content:response.response, role: 'assistant'});
    } finally {
      this.sendingMessage = false;
      this.newMessage = "";
      await this.inputElement.setFocus()
    }
  }
}
