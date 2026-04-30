import { useEffect, useRef, useState } from "react";
import jsQR from "jsqr";
import Button from "../../components/common/Button";

export default function QrScannerPanel({ onDetected, autoStart = false }) {
  const [active, setActive] = useState(false);
  const [error, setError] = useState("");
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const frameRef = useRef(null);
  const detectorRef = useRef(null);
  const startedRef = useRef(false);

  const hasCameraAccess = typeof navigator !== "undefined" && Boolean(navigator.mediaDevices?.getUserMedia);
  const hasNativeDetector = typeof window !== "undefined" && "BarcodeDetector" in window;
  const isSecureContextAvailable = typeof window === "undefined" ? true : window.isSecureContext;

  useEffect(() => {
    return () => stopScanner();
  }, []);

  useEffect(() => {
    if (!autoStart || startedRef.current) return;
    startedRef.current = true;
    startScanner();
  }, [autoStart]);

  useEffect(() => {
    if (!active || !videoRef.current || !streamRef.current) {
      return undefined;
    }

    let cancelled = false;
    const videoElement = videoRef.current;

    const attachStream = async () => {
      try {
        videoElement.srcObject = streamRef.current;
        await waitForVideoMetadata(videoElement);
        if (cancelled) return;
        await videoElement.play();
      } catch (videoError) {
        if (cancelled) return;
        setError(getCameraErrorMessage(videoError));
        stopScanner();
      }
    };

    attachStream();

    return () => {
      cancelled = true;
    };
  }, [active]);

  useEffect(() => {
    if (!active || !videoRef.current || !streamRef.current) {
      return undefined;
    }

    let cancelled = false;

    const scanFrame = async () => {
      if (cancelled || !videoRef.current) return;
      try {
        if (videoRef.current.readyState >= 2) {
          const rawValue = await detectQrValue(videoRef.current);
          if (rawValue) {
            stopScanner();
            onDetected(rawValue);
            return;
          }
        }
      } catch (scanError) {
        setError(scanError.message || "Unable to scan QR code from camera feed.");
        stopScanner();
        return;
      }
      frameRef.current = window.requestAnimationFrame(scanFrame);
    };

    frameRef.current = window.requestAnimationFrame(scanFrame);
    return () => {
      cancelled = true;
      if (frameRef.current) {
        window.cancelAnimationFrame(frameRef.current);
        frameRef.current = null;
      }
    };
  }, [active, onDetected]);

  async function startScanner() {
    if (!hasCameraAccess) {
      setError("This browser does not allow camera access for QR scanning. Use manual search instead.");
      return;
    }
    if (!isSecureContextAvailable) {
      setError("Camera access requires HTTPS or localhost. Open this app on http://localhost:5173 or run it over HTTPS.");
      return;
    }

    setError("");
    stopScanner();

    try {
      detectorRef.current = hasNativeDetector ? new window.BarcodeDetector({ formats: ["qr_code"] }) : null;
      const stream = await getCameraStream();
      streamRef.current = stream;
      setActive(true);
    } catch (cameraError) {
      setActive(false);
      setError(getCameraErrorMessage(cameraError));
      stopScanner();
    }
  }

  async function getCameraStream() {
    const preferredConstraints = [
      { video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false },
      { video: { width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false },
      { video: true, audio: false },
    ];

    let lastError = null;
    for (const constraints of preferredConstraints) {
      try {
        return await navigator.mediaDevices.getUserMedia(constraints);
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError || new Error("Unable to open the laptop camera.");
  }

  async function detectQrValue(videoElement) {
    if (detectorRef.current) {
      const detections = await detectorRef.current.detect(videoElement);
      return detections.find((item) => item.rawValue)?.rawValue || "";
    }

    if (!canvasRef.current) return "";
    const width = videoElement.videoWidth;
    const height = videoElement.videoHeight;
    if (!width || !height) return "";

    const canvas = canvasRef.current;
    canvas.width = width;
    canvas.height = height;

    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context) return "";

    context.drawImage(videoElement, 0, 0, width, height);
    const imageData = context.getImageData(0, 0, width, height);
    const result = jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: "attemptBoth",
    });
    return result?.data || "";
  }

  function stopScanner() {
    if (frameRef.current) {
      window.cancelAnimationFrame(frameRef.current);
      frameRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }
    setActive(false);
  }

  return (
    <div className="space-y-3">
      {!isSecureContextAvailable && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Camera access is blocked on non-secure pages. Open the app on `localhost` or HTTPS instead of a raw LAN IP.
        </div>
      )}
      <div className="flex gap-3">
        <Button type="button" variant="secondary" onClick={startScanner}>
          {active ? "Camera Live" : "Start Live Camera"}
        </Button>
        {active && (
          <Button type="button" variant="secondary" onClick={stopScanner}>
            Stop Scan
          </Button>
        )}
      </div>
      {error && <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
      {active && (
        <div className="overflow-hidden rounded-[2rem] border border-stone-200 bg-stone-950 p-3">
          <video ref={videoRef} className="aspect-video w-full rounded-[1.5rem] object-cover" autoPlay muted playsInline />
          <canvas ref={canvasRef} className="hidden" />
          <div className="mt-3 text-sm text-stone-300">Point the camera at the visitor QR code. Lookup will run automatically once detected.</div>
        </div>
      )}
    </div>
  );
}

function getCameraErrorMessage(error) {
  switch (error?.name) {
    case "NotAllowedError":
    case "PermissionDeniedError":
      return "Camera permission was denied. Allow camera access in your browser site settings and try again.";
    case "NotFoundError":
    case "DevicesNotFoundError":
      return "No camera device was found on this laptop.";
    case "NotReadableError":
    case "TrackStartError":
      return "The camera is busy in another app or browser tab. Close the other camera app and try again.";
    case "SecurityError":
      return "Camera access is blocked by browser security. Use localhost or HTTPS.";
    case "OverconstrainedError":
    case "ConstraintNotSatisfiedError":
      return "The preferred camera could not be opened. Retry and the app will use a simpler camera mode.";
    default:
      return error?.message || "Unable to access the camera.";
  }
}

function waitForVideoMetadata(videoElement) {
  if (videoElement.readyState >= 1) {
    return Promise.resolve();
  }

  return new Promise((resolve, reject) => {
    const handleLoadedMetadata = () => {
      cleanup();
      resolve();
    };
    const handleError = () => {
      cleanup();
      reject(new Error("Unable to start the camera preview."));
    };
    const cleanup = () => {
      videoElement.removeEventListener("loadedmetadata", handleLoadedMetadata);
      videoElement.removeEventListener("error", handleError);
    };

    videoElement.addEventListener("loadedmetadata", handleLoadedMetadata, { once: true });
    videoElement.addEventListener("error", handleError, { once: true });
  });
}
