import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error('Missing Supabase credentials in environment variables');
}

const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const {
      trackingNo, branchName, senderName, receiverName, receiverArea,
      regionType, itemName, weightKg, widthCm, heightCm, depthCm,
      billedWeightKg, sizeGrade, price, etaDate,
    } = req.body;

    // 필수값 검증
    if (!trackingNo || !senderName || !receiverName || !receiverArea || !itemName) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Supabase에 저장
    const { data, error } = await supabase
      .from('shipments')
      .insert([{
        tracking_no: trackingNo,
        sender_name: senderName,
        receiver_name: receiverName,
        receiver_area: receiverArea,
        region_type: regionType,
        item_name: itemName,
        weight_kg: weightKg,
        width_cm: widthCm,
        height_cm: heightCm,
        depth_cm: depthCm,
        billed_weight_kg: billedWeightKg,
        size_grade: sizeGrade,
        price: price,
        eta_date: etaDate,
      }])
      .select();

    if (error) {
      console.error('Supabase insert error:', error);
      return res.status(500).json({ error: error.message });
    }

    return res.status(200).json({
      success: true,
      message: '접수가 완료되었습니다',
      data: data[0],
    });
  } catch (err) {
    console.error('API error:', err);
    return res.status(500).json({ error: err.message });
  }
}
