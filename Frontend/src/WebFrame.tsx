import React from 'react'
import Webcam from "react-webcam";

import { useEffect, useRef, useState, useCallback } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import gif from "./Assest/giphy.gif";
const WebFrame = () => {
   const webCamRef = useRef<Webcam>(null);

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
      console.log(`Sending frame at ${new Date().getTime()}`);
      sendMessage(base64Data);
    } else {
      console.log(imageSrc);
    }
  };

  const retake = () => {
    setImgSrc(null);
  };

  useEffect(() => {
    if (lastMessage?.data) {
      console.log(`Received frame at ${new Date().getTime()}`);
      setRecievedFrame(lastMessage.data);
    }
  }, [lastMessage]);

  useEffect(() => {
    if (start) {
      console.log("Here");
      const tempInterval = setInterval(() => {
        const capturedBase64 = capture();
        handleClickSendMessage(capturedBase64 ? capturedBase64 : null);
      }, 300);

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
      <div className="main flex h-screen w-screen items-center justify-center gap-4">
        {/* <div className="flex flex-col items-center justify-center gap-2"> */}

        {/* Did absolute to remove our live web-cam feed and just show the recieved frames.*/}
        <div className=" flex flex-col items-center justify-center">
          <Webcam
            ref={webCamRef}
            screenshotFormat="image/jpeg"
            mirrored={true}
            className="absolute -z-10 opacity-0"
          />
        </div>
        <div className="web-cam">
          <div className="side-content">
            <img src={gif} alt="" />
          </div>
          {recievedFrame ? (
            <img src={`data:image/jpeg;base64,${recievedFrame}`} alt="" />
          ) : null}
        </div>
        <div className="buts flex justify-center gap-4">
          {" "}
          <button
            className="border-4 border-black p-2"
            onClick={() => {
              setStart(true);
            }}
          >
            <span className="shadow"></span>
            <span className="edge"></span>
            <span className="front text"> Start</span>
          </button>
          <button
            className="border-4 border-black p-2"
            onClick={() => {
              setStart(false);
            }}
          >
            <span className="shadow"></span>
            <span className="edge"></span>
            <span className="front text"> Stop</span>
          </button>
        </div>
      </div>
      {/* </div> */}
    </>
  );
}


export default WebFrame