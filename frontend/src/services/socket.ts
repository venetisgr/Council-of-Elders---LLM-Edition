import { io, Socket } from "socket.io-client";
import { getBackendUrl } from "./api";

let socket: Socket | null = null;

export function getSocket(): Socket {
  if (!socket) {
    const backendUrl = getBackendUrl();

    socket = io(backendUrl || undefined, {
      autoConnect: false,
      transports: ["websocket", "polling"],
    });
  }
  return socket;
}

export function connectSocket(): Socket {
  const s = getSocket();
  if (!s.connected) {
    s.connect();
  }
  return s;
}

export function disconnectSocket(): void {
  if (socket?.connected) {
    socket.disconnect();
  }
}
