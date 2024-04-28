/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_chat_audio_endpoint_chat_audio_post } from '../models/Body_chat_audio_endpoint_chat_audio_post';
import type { Body_login_for_access_token_token_post } from '../models/Body_login_for_access_token_token_post';
import type { Body_upload_photo_upload_photo_post } from '../models/Body_upload_photo_upload_photo_post';
import type { ChatMessage } from '../models/ChatMessage';
import type { ChatResponse } from '../models/ChatResponse';
import type { Token } from '../models/Token';
import type { User } from '../models/User';
import type { UserCreate } from '../models/UserCreate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Login For Access Token
     * @param formData
     * @returns Token Successful Response
     * @throws ApiError
     */
    public static loginForAccessTokenTokenPost(
        formData: Body_login_for_access_token_token_post,
    ): CancelablePromise<Token> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/token',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Users Me
     * @returns User Successful Response
     * @throws ApiError
     */
    public static readUsersMeUsersMeGet(): CancelablePromise<User> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/me/',
        });
    }
    /**
     * Create User
     * @param requestBody
     * @returns Token Successful Response
     * @throws ApiError
     */
    public static createUserUsersPost(
        requestBody: UserCreate,
    ): CancelablePromise<Token> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/users/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Chat Audio Endpoint
     * @param formData
     * @returns ChatResponse Successful Response
     * @throws ApiError
     */
    public static chatAudioEndpointChatAudioPost(
        formData: Body_chat_audio_endpoint_chat_audio_post,
    ): CancelablePromise<ChatResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/chat-audio',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Chat Endpoint
     * @param requestBody
     * @returns ChatResponse Successful Response
     * @throws ApiError
     */
    public static chatEndpointChatPost(
        requestBody: Array<ChatMessage>,
    ): CancelablePromise<ChatResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/chat',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Audio
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAudioAudioGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/audio',
        });
    }
    /**
     * Upload Photo
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static uploadPhotoUploadPhotoPost(
        formData: Body_upload_photo_upload_photo_post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/upload_photo',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
