import React, { useState, useRef } from "react";
import { useReactToPrint } from "react-to-print";
import './App.css'
const App = () => {
  const [formData, setFormData] = useState({
    subject: "",
    petitioner: "",
    respondent: "",
    summary: "",
  });

  const [pilOutput, setPilOutput] = useState("");
  const textAreaRef = useRef(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleVoiceInput = (field) => {
    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = (event) => {
      const voiceText = event.results[0][0].transcript;
      setFormData((prev) => ({ ...prev, [field]: voiceText }));
    };
  };

  const handleSubmit = async () => {
    const response = await fetch("http://127.0.0.1:5000/run_pil_generator", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    const data = await response.json();
    setPilOutput(data["pil_text"]);
  };

  const handleDownloadPDF = useReactToPrint({
    content: () => textAreaRef.current,
    documentTitle: "PIL_Document",
  });

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-5">
      <h1 className="text-3xl font-bold mb-5">PIL Generator</h1>

      {["subject", "petitioner", "respondent", "summary"].map((field) => (
        <div key={field} className="w-full max-w-lg mb-4">
          <label className="block text-lg font-semibold mb-1">{field.toUpperCase()}</label>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              name={field}
              value={formData[field]}
              onChange={handleChange}
              className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
              placeholder={`Enter ${field}`}
            />
            <button
              onClick={() => handleVoiceInput(field)}
              className="p-2 bg-blue-500 text-white rounded hover:bg-blue-700"
            >
              🎤
            </button>
          </div>
        </div>
      ))}

      <button
        onClick={handleSubmit}
        className="mt-4 px-6 py-2 bg-blue-600 text-white font-semibold rounded hover:bg-blue-800"
      >
        Generate PIL
      </button>

      {pilOutput && (
        <div className="w-full max-w-lg mt-6">
          <label className="block text-lg font-semibold mb-1">Editable PIL</label>
          <textarea
            ref={textAreaRef}
            value={pilOutput}
            onChange={(e) => setPilOutput(e.target.value)}
            className="w-full p-3 border rounded h-40 focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleDownloadPDF}
            className="mt-3 px-6 py-2 bg-green-600 text-white font-semibold rounded hover:bg-green-800"
          >
            Download as PDF
          </button>
        </div>
      )}
    </div>
  );
};

export default App;
