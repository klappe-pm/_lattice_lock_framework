import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { wsClient } from '../websocket';

// Mock WebSocket class
class MockWebSocket {
    constructor(url) {
        this.url = url;
        this.readyState = 0; // CONNECTING
        this.send = vi.fn();
        this.close = vi.fn();
        setTimeout(() => {
             this.readyState = 1; // OPEN
             if (this.onopen) this.onopen();
        }, 10);
    }
}

// Attach OPEN/CONNECTING constants
MockWebSocket.CONNECTING = 0;
MockWebSocket.OPEN = 1;
MockWebSocket.CLOSING = 2;
MockWebSocket.CLOSED = 3;

vi.stubGlobal('WebSocket', MockWebSocket);

describe('WebSocketClient', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        wsClient.disconnect();
        wsClient.isConnecting = false;
        wsClient.reconnectAttempts = 0;
        
        // Ensure mock socket logic doesn't leak
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('should connect only once', () => {
        wsClient.connect('ws://test');
        expect(wsClient.isConnecting).toBe(true);
        
        // Try connecting again (should return early)
        wsClient.connect('ws://test');
        expect(wsClient.isConnecting).toBe(true);
        
        // Fast forward to open
        vi.advanceTimersByTime(20);
        expect(wsClient.isConnected).toBe(true);
        expect(wsClient.isConnecting).toBe(false);
    });

    it('should handle messages', () => {
        wsClient.connect('ws://test');
        vi.advanceTimersByTime(20);

        const handler = vi.fn();
        wsClient.on('test_event', handler);
        
        // Simulate message
        const msg = { type: 'test_event', payload: 'data' };
        wsClient.socket.onmessage({ data: JSON.stringify(msg) });
        
        expect(handler).toHaveBeenCalledWith('data');
    });

    it('should handle catch-all listener', () => {
        wsClient.connect('ws://test');
        vi.advanceTimersByTime(20);

        const handler = vi.fn();
        wsClient.on('*', handler);
        
        const msg = { type: 'any', payload: 'data' };
        wsClient.socket.onmessage({ data: JSON.stringify(msg) });
        
        expect(handler).toHaveBeenCalledWith(msg);
    });
    
    it('should send messages', () => {
        wsClient.connect('ws://test');
        vi.advanceTimersByTime(20); // Connected
        
        wsClient.send('my_type', { val: 1 });
        expect(wsClient.socket.send).toHaveBeenCalledWith(JSON.stringify({ type: 'my_type', payload: { val: 1 } }));
    });
    
    it('should warn if sending while disconnected', () => {
        const spy = vi.spyOn(console, 'warn').mockImplementation(() => {});
        wsClient.socket = null; // Ensure disconnected
        
        wsClient.send('type', {});
        expect(spy).toHaveBeenCalledWith(expect.stringContaining('Not connected'));
    });

    it('should attempt reconnect on close', () => {
        wsClient.connect('ws://test');
        vi.advanceTimersByTime(20); // Connected
        
        // Simulate close
        wsClient.socket.readyState = MockWebSocket.CLOSED;
        wsClient.socket.onclose({ code: 1006 });
        
        // Reconnect logic uses setTimeout
        vi.advanceTimersByTime(1000); // 1st attempt delay
        
        // Check attempts instead of isConnecting timing which is racy
        expect(wsClient.reconnectAttempts).toBe(1);
    });

    it('should stop reconnecting after max attempts', () => {
        wsClient.connect('ws://test');
        vi.advanceTimersByTime(20);
        
        const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
        
        wsClient.reconnectAttempts = 5;
        wsClient.attemptReconnect('ws://test');
        
        expect(spy).toHaveBeenCalledWith(expect.stringContaining('Max reconnect attempts reached'));
    });
    
    it('should handle parse errors', () => {
        wsClient.connect('ws://test');
        vi.advanceTimersByTime(20);
        
        const spy = vi.spyOn(console, 'error');
        wsClient.socket.onmessage({ data: 'invalid json' });
        expect(spy).toHaveBeenCalledWith(expect.stringContaining('Parse error'), expect.anything());
    });
    
    it('should subscribe to execution', () => {
        wsClient.connect();
        vi.advanceTimersByTime(20);
        
        wsClient.subscribeToExecution('123');
        expect(wsClient.socket.send).toHaveBeenCalledWith(JSON.stringify({ 
            type: 'subscribe_execution', 
            payload: { execution_id: '123' } 
        }));
    });
    
    it('should cleanup listeners', () => {
        const handler = vi.fn();
        const unsub = wsClient.on('event', handler);
        unsub();
        
        wsClient.emit('event', 'payload');
        expect(handler).not.toHaveBeenCalled();
    });
});
