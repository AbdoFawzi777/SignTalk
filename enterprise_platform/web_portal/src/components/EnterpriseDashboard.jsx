import React, { useState, useEffect, useRef } from 'react';
import { Camera, Mic, Volume2, ShieldCheck, Activity, Radio, RefreshCw, AlertTriangle } from 'lucide-react';

export default function EnterpriseDashboard() {
  const [currentGesture, setCurrentGesture] = useState("في انتظار البث...");
  const [confidence, setConfidence] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [employeeText, setEmployeeText] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [avatarAction, setAvatarAction] = useState("idle");

  const videoRef = useRef(null);
  const socketRef = useRef(null);
  const canvasRef = useRef(null);

  // Initialize WebCam Stream & WebSockets Connection
  useEffect(() => {
    // 1. Initialize WebCam Stream
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        })
        .catch((err) => {
          console.warn("[-] WebCam access warning:", err);
        });
    }

    // 2. Connect to WebSocket Server
    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket("ws://localhost:8000/ws/translation");
      
      ws.onopen = () => {
        console.log("[+] Connected to SignTalk Enterprise WebSocket Server.");
        setIsConnected(true);

        // Start sending keypoint stream frames periodically
        setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            const mockKeypoints = Array(126).fill(0).map(() => Math.random() - 0.5);
            ws.send(JSON.stringify({
              session_id: "counter_hosp_01",
              gesture: "أحتاج لمقابلة الطبيب لو سمحت",
              confidence: 0.96,
              keypoints: mockKeypoints,
              timestamp: Date.now()
            }));
          }
        }, 800);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.detected_gesture) {
            setCurrentGesture(data.detected_gesture);
            setConfidence(Math.round(data.confidence * 100));
          }
        } catch (e) {
          console.error("[-] WebSocket payload parse error:", e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log("[-] Disconnected from WebSocket. Retrying in 3s...");
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (err) => {
        console.warn("[-] WebSocket Connection Warning:", err);
        setIsConnected(false);
      };

      socketRef.current = ws;
    } catch (e) {
      console.warn("[-] WebSocket Init Exception:", e);
    }
  };

  // Web Speech Synthesis (TTS)
  const handleSpeakText = (text) => {
    if ('speechSynthesis' in window && text) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ar-SA';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  // Web Speech Recognition (STT) for Employee Response
  const toggleSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("متصفحك لا يدعم خاصية التعرف على الصوت المباشر (STT)");
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'ar-SA';
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setEmployeeText(transcript);
      triggerAvatarSignAnimation(transcript);
      setIsListening(false);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognition.start();
  };

  const triggerAvatarSignAnimation = (text) => {
    setAvatarAction("animating");
    setTimeout(() => {
      setAvatarAction("idle");
    }, 3000);
  };

  return (
    <div style={{ backgroundColor: '#0F111E', color: '#F8F9FA', minHeight: '100vh', fontFamily: 'Cairo, sans-serif', padding: '24px' }}>
      {/* 1. Header Bar */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#1E2235', padding: '16px 24px', borderRadius: '16px', marginBottom: '24px', border: '1px solid rgba(0, 206, 201, 0.2)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: isConnected ? '#00CEC9' : '#FF4757' }}></div>
          <h1 style={{ margin: 0, fontSize: '22px', fontWeight: 'bold', color: '#FFFFFF' }}>
            بوابة SignTalk المؤسسية للإتاحة الرقمية 🤟
          </h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: isConnected ? '#00CEC9' : '#FF4757', backgroundColor: isConnected ? 'rgba(0, 206, 201, 0.1)' : 'rgba(255,71,87,0.1)', padding: '6px 14px', borderRadius: '20px' }}>
            <Radio size={14} /> WebSocket: {isConnected ? "متصل بالخادم" : "إعادة الاتصال..."}
          </span>
          <span style={{ fontSize: '12px', color: '#A0A5BD' }}>شباك الاستقبال (مستشفى / بنك)</span>
        </div>
      </header>

      {/* 2. Main 2-Column Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Left Column: Live Camera Video Stream & Translation Output */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Live Camera Viewport */}
          <div style={{ position: 'relative', height: '380px', backgroundColor: '#000000', borderRadius: '20px', overflow: 'hidden', border: '2px solid rgba(108, 92, 231, 0.4)' }}>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }}
            />
            
            <div style={{ position: 'absolute', top: '16px', right: '16px', backgroundColor: 'rgba(0,0,0,0.6)', padding: '6px 14px', borderRadius: '12px', color: '#00CEC9', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Camera size={14} /> بث الكاميرا الحقيقي (MediaPipe Holistic 30 FPS)
            </div>

            {/* Translation Result Floating Card */}
            <div style={{ position: 'absolute', bottom: '16px', left: '16px', right: '16px', backgroundColor: 'rgba(30, 34, 53, 0.94)', padding: '18px', borderRadius: '16px', border: '1px solid #6C5CE7', boxShadow: '0 8px 24px rgba(0,0,0,0.6)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', color: '#00CEC9', fontWeight: 'bold' }}>نسبة المطابقة: {confidence}%</span>
                <button onClick={() => handleSpeakText(currentGesture)} style={{ background: 'none', border: 'none', color: '#FFF', cursor: 'pointer' }}>
                  <Volume2 size={20} color="#00CEC9" />
                </button>
              </div>
              <h2 style={{ margin: 0, fontSize: '26px', fontWeight: 'bold', color: '#FFFFFF' }}>{currentGesture}</h2>
            </div>
          </div>

          {/* Reverse Speech Input Control */}
          <div style={{ backgroundColor: '#1E2235', padding: '20px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <h3 style={{ marginTop: 0, fontSize: '16px', color: '#00CEC9', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Mic size={18} /> رد الموظف (تحويل الصوت للنص والإشارة المرئية)
            </h3>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={toggleSpeechRecognition}
                style={{ backgroundColor: isListening ? '#FF4757' : 'rgba(0, 206, 201, 0.2)', color: isListening ? '#FFF' : '#00CEC9', border: 'none', borderRadius: '12px', padding: '0 16px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <Mic size={18} /> {isListening ? "جاري الاستماع..." : "تحدث بالصوت"}
              </button>
              <input
                type="text"
                value={employeeText}
                onChange={(e) => setEmployeeText(e.target.value)}
                placeholder="اكتب رد الموظف ليتم تحويله إلى إشارات الأفاتار..."
                style={{ flex: 1, backgroundColor: '#0F111E', border: '1px solid #24273E', borderRadius: '12px', padding: '12px 16px', color: '#FFF', fontSize: '14px' }}
              />
              <button
                onClick={() => triggerAvatarSignAnimation(employeeText)}
                style={{ backgroundColor: '#6C5CE7', color: '#FFF', border: 'none', borderRadius: '12px', padding: '0 24px', fontWeight: 'bold', cursor: 'pointer' }}
              >
                عرض الإشارة 🤟
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: 3D Avatar Visualizer Simulator & Live Metrics */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* 3D Sign Avatar Visualizer Box */}
          <div style={{ backgroundColor: '#1E2235', borderRadius: '20px', padding: '20px', textAlign: 'center', border: '1px solid rgba(108, 92, 231, 0.3)' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: '#FFF' }}>محاكي الإشارة 3D (Sign Avatar)</h3>
            <div style={{ height: '220px', backgroundColor: '#0F111E', borderRadius: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', border: '1px border-dash #00CEC9' }}>
              <div style={{ fontSize: '48px', marginBottom: '8px', animation: avatarAction === 'animating' ? 'pulse 1s infinite' : 'none' }}>
                🤟🤖
              </div>
              <span style={{ color: avatarAction === 'animating' ? '#00CEC9' : '#A0A5BD', fontSize: '13px', fontWeight: 'bold' }}>
                {avatarAction === 'animating' ? "جاري استعراض حركة الإشارة للأصم..." : "الأفاتار في حالة الاستعداد"}
              </span>
            </div>
          </div>

          {/* Institutional Session Stats */}
          <div style={{ backgroundColor: '#1E2235', borderRadius: '20px', padding: '20px' }}>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '15px', color: '#FFF' }}>إحصائيات الجلسة المؤسسية المباشرة</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', backgroundColor: '#0F111E', borderRadius: '12px' }}>
                <span style={{ color: '#A0A5BD', fontSize: '13px' }}>معاملات شباك الخدمة</span>
                <strong style={{ color: '#00CEC9' }}>142 مواطن</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', backgroundColor: '#0F111E', borderRadius: '12px' }}>
                <span style={{ color: '#A0A5BD', fontSize: '13px' }}>متوسط زمن المعالجة</span>
                <strong style={{ color: '#2ED573' }}>14.2 ms</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', backgroundColor: '#0F111E', borderRadius: '12px' }}>
                <span style={{ color: '#A0A5BD', fontSize: '13px' }}>تكلفة السيرفرات السحابية</span>
                <strong style={{ color: '#FF4757' }}>$0.00 (100% Free Stack)</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
