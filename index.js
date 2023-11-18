const express = require("express");
const multer = require("multer");
const { exec } = require("child_process");
const path = require("path");
const app = express();
const port = 3000;

// Set up multer for handling file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Define the storage location for uploaded files
const uploadPath = path.join(__dirname, "uploads");
const pythonScriptPath = path.join(__dirname, "background.py");

// Ensure the 'uploads' directory exists
const fs = require("fs");
if (!fs.existsSync(uploadPath)) {
  fs.mkdirSync(uploadPath);
}

app.post(
  "/processVideo",
  upload.fields([
    { name: "video", maxCount: 1 },
    { name: "background", maxCount: 1 },
  ]),
  (req, res) => {
    const videoBuffer = req.files["video"][0].buffer;
    const backgroundBuffer = req.files["background"][0].buffer;

    // Save uploaded files to the server
    const videoFilePath = path.join(uploadPath, "uploaded_video.mp4");
    const backgroundFilePath = path.join(uploadPath, "uploaded_background.jpg");

    fs.writeFileSync(videoFilePath, videoBuffer);
    fs.writeFileSync(backgroundFilePath, backgroundBuffer);

    // Execute the Python script as a child process
    const command = `py ${pythonScriptPath} ${videoFilePath} ${backgroundFilePath}`;
    const outputVideoPath = path.resolve(__dirname, "output_video.mp4");
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing Python script: ${error}`);
        res.status(500).send("Internal Server Error");
      } else {
        // Send the processed video as a response
        res.status(200).sendFile(outputVideoPath);
        fs.unlinkSync(videoFilePath);
        fs.unlinkSync(backgroundFilePath);
      }
    });
  }
);

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
