# API Endpoints Documentation

The provided API facilitates real-time communication and data retrieval for a HealthMate chat. Below is the documentation for the available endpoints that frontend developers can use to integrate with the backend services effectively.

## WebSocket Endpoint

### Endpoint: `/ws/`

This endpoint establishes a WebSocket connection to enable real-time bi-directional communication between the client (frontend) and the server (backend).

#### Parameters:

- `session_id` (Optional): A string parameter that represents the ID of an existing chat session. If provided, the connection will resume the specified session.
- `token`: A query parameter representing the user's authentication token, used to identify and authenticate the current user.

#### Functionality:

1. **Connection Establishment**: The frontend initiates a WebSocket connection by connecting to this endpoint. The backend accepts the connection and establishes a persistent communication channel.
2. **User Authentication**: The user is authenticated using the provided `token`. If authentication fails, the connection should be closed with an appropriate error message.
3. **Session Initialization**: If a `session_id` is provided, the backend retrieves the corresponding chat history. If no `session_id` is provided, a new chat session is initiated.
4. **Real-time Communication**: Once the connection is established and the session is initialized, the frontend can send messages through the WebSocket. The backend processes these messages using the Gemini logic and returns the responses in real-time.

## RESTful Endpoints

### Endpoint: `/all_chat/`

This endpoint retrieves all chat sessions associated with the authenticated user.

#### Method: `GET`

#### Parameters:

- `db`: A dependency that injects the session object to interact with the database.
- `current_user`: A dependency that determines the current user based on the authentication context.

#### Response:

- A list of chat session summaries, where each summary includes:
  - `title`: The first message of the chat session.
  - `date`: The creation date of the chat session.
  - `id`: The unique identifier of the chat session.

#### Usage:

This endpoint is used to retrieve a summary of all chat sessions associated with the current user. It can be utilized to display a history of interactions or to allow users to revisit previous conversations.

### Usage Example:

Frontend developers can use these endpoints to create a dynamic and interactive chat interface. For instance, upon loading the chat interface, the frontend can connect to the WebSocket endpoint to either start a new session or resume an existing one. As the user interacts with the interface, messages are sent and received through this WebSocket connection, enabling real-time communication. Concurrently, the frontend can  query the `/all_chat/` endpoint to display past interactions.
