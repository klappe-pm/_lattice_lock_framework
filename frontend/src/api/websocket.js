/**
 * WebSocket client for real-time execution updates
 */

class WebSocketClient {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.isConnecting = false;
  }

  /**
   * Connect to WebSocket server
   * @param {string} url - WebSocket URL
   */
  connect(url = `ws://${window.location.host}/ws`) {
    if (this.socket?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    try {
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        console.log('[WS] Connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.emit('connected');
      };

      this.socket.onclose = (event) => {
        console.log('[WS] Disconnected', event.code);
        this.isConnecting = false;
        this.emit('disconnected');
        this.attemptReconnect(url);
      };

      this.socket.onerror = (error) => {
        console.error('[WS] Error:', error);
        this.emit('error', error);
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('[WS] Parse error:', error);
        }
      };
    } catch (error) {
      console.error('[WS] Connection error:', error);
      this.isConnecting = false;
      this.attemptReconnect(url);
    }
  }

  /**
   * Attempt to reconnect after disconnection
   */
  attemptReconnect(url) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * this.reconnectAttempts;
    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      this.connect(url);
    }, delay);
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(data) {
    const { type, payload } = data;

    // Emit to specific event listeners
    if (type && this.listeners.has(type)) {
      this.listeners.get(type).forEach((callback) => callback(payload));
    }

    // Emit to catch-all listeners
    if (this.listeners.has('*')) {
      this.listeners.get('*').forEach((callback) => callback(data));
    }
  }

  /**
   * Subscribe to an event
   * @param {string} event - Event type
   * @param {Function} callback - Callback function
   * @returns {Function} Unsubscribe function
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  /**
   * Emit an event locally
   */
  emit(event, payload) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback) => callback(payload));
    }
  }

  /**
   * Send a message to the server
   * @param {string} type - Message type
   * @param {Object} payload - Message payload
   */
  send(type, payload) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type, payload }));
    } else {
      console.warn('[WS] Not connected, cannot send message');
    }
  }

  /**
   * Subscribe to execution updates
   * @param {string} executionId - Execution to subscribe to
   */
  subscribeToExecution(executionId) {
    this.send('subscribe_execution', { execution_id: executionId });
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.listeners.clear();
  }

  /**
   * Check if connected
   */
  get isConnected() {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}

export const wsClient = new WebSocketClient();
export default wsClient;
