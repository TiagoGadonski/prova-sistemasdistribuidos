import express from 'express';
import axios   from 'axios';
import { createClient } from 'redis';
import dotenv  from 'dotenv';
dotenv.config();

const app  = express();
app.use(express.json());

const redis = createClient({ url: process.env.REDIS_URL });
await redis.connect();

/* GET /sensor-data -------------------------------------------------------- */
app.get('/sensor-data', async (_, res) => {
  const key = 'sensor:data';
  const cached = await redis.get(key);
  if (cached) return res.json(JSON.parse(cached));

  const data = {
    temperature: (20 + Math.random() * 30).toFixed(2), // °C
    pressure:    (150 + Math.random() * 50).toFixed(2) // bar
  };
  await redis.setEx(key, process.env.CACHE_TTL, JSON.stringify(data));
  res.json(data);
});

/* POST /alert ------------------------------------------------------------- */
app.post('/alert', async (req, res) => {
  try {
    await axios.post(process.env.EVENTS_API, req.body);
    res.status(202).json({ msg: 'Alerta enviado ao módulo Python' });
  } catch (err) {
    res.status(500).json({ error: 'Falha ao encaminhar alerta' });
  }
});

app.listen(process.env.PORT, () =>
  console.log(`Sensor API 🔊  http://localhost:${process.env.PORT}`)
);
