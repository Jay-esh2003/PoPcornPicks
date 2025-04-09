# PopcornPicks 
A movie recommendation app that uses deep learning and embedding similarity to give personalized suggestions based on movies you select.

## 🔥 Features
- Searchable movie picker with real titles
- Deep learning-based recommendations (embedding similarity)
- Movie posters powered by TMDB API
- Responsive UI with poster grid
- Flask + JavaScript full-stack integration

## 📦 Tech Stack
- Python (Flask)
- TensorFlow / Keras
- JavaScript, HTML, CSS
- TMDB API, MovieLens dataset

## 🚀 How to Run Locally
1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/PopcornPicks.git
   cd PopcornPicks
   ```
2. Create `.env` file:
   ```bash
   echo "TMDB_API_KEY=your_api_key_here" > .env
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python app.py
   ```

Visit [http://localhost:5000](http://localhost:5000)

## 🌐 Deployment
Deployed via [Render](https://render.com). Set `TMDB_API_KEY` as an environment variable.