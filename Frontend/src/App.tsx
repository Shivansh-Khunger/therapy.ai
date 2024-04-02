import Webcam from "react-webcam";
import { useEffect, useRef, useState, useCallback } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import b64toBlob from "b64-to-blob";

function App() {
  const webCamRef = useRef<Webcam>(null);

  const [imgSrc, setImgSrc] = useState<string | null>(null);
  const [socketUrl, setSocketUrl] = useState("ws://127.0.0.1:9080/ws");
  const [messageHistory, setMessageHistory] = useState<MessageEvent<any>[]>([]);
  const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl, {});

  const capture = useCallback(() => {
    const imageSrc = webCamRef.current?.getScreenshot();
    if (imageSrc) {
      setImgSrc(imageSrc);
    } else {
      console.log(`imageSrc is not assignable`);
    }
  }, [webCamRef]);

  const handleClickSendMessage = useCallback(async () => {
    if (imgSrc) {
      let imageSrcParts = imgSrc.split(",");
      let base64Data = imageSrcParts[1];
      console.log(base64Data);
      const blob = b64toBlob(base64Data, "image/jpeg");

      console.log(blob);
      sendMessage(blob);
    } else {
      console.log(imgSrc);
    }
  }, [imgSrc]);

  const retake = () => {
    setImgSrc(null);
  };

  const connectionStatus = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  }[readyState];

  useEffect(() => {
    console.log(connectionStatus);
  }, [connectionStatus]);

  return (
    <>
      <div className="flex h-screen w-screen items-center justify-center gap-4">
        <div className="flex flex-col items-center justify-center">
          <h2 className="flex justify-center font-bold">Our Webcam</h2>
          <Webcam ref={webCamRef} screenshotFormat="image/jpeg" />
        </div>

        <button onClick={capture} className="absolute top-32">
          Capture
        </button>
        <button
          className="absolute left-4 top-32"
          onClick={handleClickSendMessage}
        >
          Send
        </button>
      </div>
    </>
  );
}

export default App;
