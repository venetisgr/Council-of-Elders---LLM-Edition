import { useEffect } from "react";
import { getSocket } from "@/services/socket";
import { useDebateStore } from "@/stores/debateStore";
import { DebateStatus } from "@/types";

export function useDebateConnection() {
  const status = useDebateStore((s) => s.status);

  useEffect(() => {
    const socket = getSocket();

    const handleConnect = () => {
      console.log("[Agora] Socket connected:", socket.id);
    };

    const handleDisconnect = (reason: string) => {
      console.log("[Agora] Socket disconnected:", reason);
    };

    const handleConnectError = (err: Error) => {
      console.error("[Agora] Socket connection error:", err.message);
    };

    socket.on("connect", handleConnect);
    socket.on("disconnect", handleDisconnect);
    socket.on("connect_error", handleConnectError);

    return () => {
      socket.off("connect", handleConnect);
      socket.off("disconnect", handleDisconnect);
      socket.off("connect_error", handleConnectError);
    };
  }, [status]);

  const isConnected =
    status === DebateStatus.RUNNING || status === DebateStatus.PAUSED;

  return { isConnected };
}
