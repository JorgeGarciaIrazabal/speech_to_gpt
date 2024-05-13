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
import {micOutline, send, volumeHigh} from 'ionicons/icons';
import {MarkdownComponent} from "ngx-markdown";
import {Storage} from '@ionic/storage-angular';
import {Router} from '@angular/router'; // Import Router
import {
  VoiceRecorder,
  RecordingData,
} from 'capacitor-voice-recorder';
import { TextToSpeech } from '@capacitor-community/text-to-speech';



@Component({
  selector: 'app-chat',
  templateUrl: './chat.page.html',
  styleUrls: ['./chat.page.scss'],
  standalone: true,
  imports: [IonContent, IonHeader, IonTitle, IonToolbar, CommonModule, FormsModule, IonButtons, IonMenuButton,
    IonButton, IonList, IonItem, IonLabel, IonFooter, IonInput, IonSpinner, IonIcon, IonRow, IonGrid, IonCol,
    MarkdownComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ChatPage implements OnInit {
  messages: ChatMessage[] = [];
  newMessage: string = "";
  sendingMessage: boolean = false;
  logMessage: string = "";
  private _storage: Storage | null = null;
  @ViewChild('input') inputElement!: IonInput;

  constructor(private storage: Storage, private router: Router) {
    addIcons({send, micOutline, volumeHigh});
  }

  async ngOnInit() {
    console.log('init ChatPage')
    this._storage = await this.storage.create();
    const result = await VoiceRecorder.canDeviceVoiceRecord()
    console.log(result)

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

  async sendMessageBasic() {
    const response = await fetch(OpenAPI.BASE + '/chat', {
      method: 'POST',
      body: JSON.stringify(this.messages),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OpenAPI.TOKEN}`
      }
    });

    await this.handleResponse(response);
  }

  async sendMessage() {
    this.messages.push({content: this.newMessage, role: 'user'});
    this.sendingMessage = true;

    try {
      await this.sendMessageBasic();
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

  async startAudio() {
    const result = await VoiceRecorder.requestAudioRecordingPermission()
    await VoiceRecorder.startRecording()
    console.log("startAudio");
  }

  async sendAudio() {
    const recordingData: RecordingData = await VoiceRecorder.stopRecording();
    console.log(recordingData)
    try {
      const formData = new FormData();
      const audioBlob = this.b64toBlob(recordingData.value.recordDataBase64, recordingData.value.mimeType);
      formData.append('audio', audioBlob, 'audio');
      formData.append('messages', JSON.stringify(this.messages));
      const response = await fetch(OpenAPI.BASE + '/chat-audio', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${OpenAPI.TOKEN}`
        }
      });
      await this.handleResponse(response);
    } catch (error) {
      this.messages.pop();
      console.error(error);
    } finally {
      this.sendingMessage = false;
      this.newMessage = "";
      await this.inputElement.setFocus()
      this.logMessage = "";
    }
    console.log("sendAudio");
  }

  private async handleResponse(response: Response) {
    let message_text = ""

    if (!response.ok && response.status === 401) {
      // If the status code is 401 (unauthorized), navigate the user back to the 'login/logout' route
      await this.router.navigate(['/login/logout']);
      return;
    }

    if (response.body == null) {
      throw new Error('Response body is null');
    }
    const reader = response.body.getReader();

    while (true) {
      const {done, value} = await reader.read();
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
        } else if (this.messages.length === 0) {
          this.messages.push(message);
        } else if (message.role === this.messages[this.messages.length - 1].role) {
          this.messages[this.messages.length - 1].content += message.content;
        } else {
          this.messages.push(message);
        }
      }
      message_text = splitMessages[splitMessages.length - 1];
    }
  }

  b64toBlob(b64Data: any, contentType = '', sliceSize = 512) {
    const byteCharacters = atob(b64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
      const slice = byteCharacters.slice(offset, offset + sliceSize);

      const byteNumbers = new Array(slice.length);
      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }

      const byteArray = new Uint8Array(byteNumbers);
      byteArrays.push(byteArray);
    }

    return new Blob(byteArrays, {type: contentType});
  }

  clearChat() {
    this.messages = [];
  }

  textToSpeech(text: string) {
    let utter = new window.SpeechSynthesisUtterance(text);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);

  }
}
