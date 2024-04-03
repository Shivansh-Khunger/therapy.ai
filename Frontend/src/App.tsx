import Webcam from "react-webcam";
import { useEffect, useRef, useState, useCallback } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import b64toBlob from "b64-to-blob";

function App() {
  const webCamRef = useRef<Webcam>(null);

  // Ignore this code left only for if needed in future

  // const useRecievedFrame = (initialValue: string | null) => {
  //   const [recievedFrame, setRecievedFrame] = useState<string | null>(
  //     initialValue,
  //   );

  //   let current = recievedFrame;

  //   const get = () => current;

  //   const set = (newValue: string) => {
  //     current = newValue;
  //     setRecievedFrame(newValue);
  //     return current;
  //   };

  //   return {
  //     get,
  //     set,
  //   };
  // };

  const [imgSrc, setImgSrc] = useState<string | null>(null);
  const [socketUrl, setSocketUrl] = useState("ws://127.0.0.1:9080/ws");
  const [messageHistory, setMessageHistory] = useState<MessageEvent<any>[]>([]);
  const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl, {});
  const [start, setStart] = useState(false);
  const [recievedFrame, setRecievedFrame] = useState<string | null>(null);

  // Ignore this code left only for if needed in future
  // const rf = useRecievedFrame(null);

  const capture = () => {
    const imageSrc = webCamRef.current?.getScreenshot();

    if (imageSrc) {
      setImgSrc(imageSrc);
    } else {
      console.log(`imageSrc is not assignable`);
    }
    return imageSrc;
  };

  const handleClickSendMessage = (imageSrc: string | null) => {
    if (imageSrc) {
      let imageSrcParts = imageSrc.split(",");
      let base64Data = imageSrcParts[1];
      console.log(base64Data);
      sendMessage(base64Data);
    } else {
      console.log(imageSrc);
    }
  };

  const retake = () => {
    setImgSrc(null);
  };

  useEffect(() => {
    if (start) {
      console.log("Here");
      const tempInterval = setInterval(() => {
        const capturedBase64 = capture();
        handleClickSendMessage(capturedBase64 ? capturedBase64 : null);
      }, 100);

      return () => {
        clearInterval(tempInterval);
      };
    } else {
      console.log("Currently Stopped");
    }
  }, [start]);

  useEffect(() => {
    setRecievedFrame(lastMessage?.data);
  }, [lastMessage]);

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
          <div className="flex justify-center gap-4">
            {" "}
            <button
              className="border-4 border-black p-2"
              onClick={() => {
                setStart(true);
              }}
            >
              Start
            </button>
            <button
              className="border-4 border-black p-2"
              onClick={() => {
                setStart(false);
              }}
            >
              Stop
            </button>
          </div>
          <h2 className="flex justify-center font-bold">Our Webcam</h2>
          <Webcam
            ref={webCamRef}
            screenshotFormat="image/jpeg"
            mirrored={true}
          />
        </div>
        <div>
          {recievedFrame ? (
            <img src={`data:image/jpeg;base64,${recievedFrame}`} alt="" />
          ) : null}
        </div>
      </div>
    </>
  );
}

export default App;
