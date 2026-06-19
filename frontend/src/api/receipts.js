import client from './client'

export async function scanReceipt(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/receipts/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
