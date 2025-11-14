import type { Suggestion, SubmitResult } from '@/types/sheet';

type MockRecord = {
  id: string;
  name: string;
  code: string;
  description: string;
};

const mockDatabase: MockRecord[] = [
  { id: '1', name: '华北大区·北京', code: 'CN-110000', description: '重点客户数量 120' },
  { id: '2', name: '华东大区·上海', code: 'CN-310000', description: '重点客户数量 86' },
  { id: '3', name: '华南大区·深圳', code: 'CN-440300', description: '重点客户数量 64' },
  { id: '4', name: '华中大区·武汉', code: 'CN-420100', description: '重点客户数量 45' },
  { id: '5', name: '西南大区·成都', code: 'CN-510100', description: '重点客户数量 59' },
  { id: '6', name: '华北大区·天津', code: 'CN-120000', description: '重点客户数量 34' },
  { id: '7', name: '华南大区·广州', code: 'CN-440100', description: '重点客户数量 72' }
];

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function searchRecords(query: string): Promise<Suggestion[]> {
  await delay(380);
  const keyword = query.toLowerCase();
  return mockDatabase
    .filter((item) => item.name.toLowerCase().includes(keyword) || item.code.toLowerCase().includes(keyword))
    .slice(0, 6)
    .map((item) => ({
      id: item.id,
      label: `${item.name} (${item.code})`,
      value: item.code,
      description: item.description
    }));
}

export async function submitSheet(data: string[][]): Promise<SubmitResult> {
  await delay(600);
  const hasInvalidRow = data.some((row) => row.every((cell) => cell === ''));
  if (hasInvalidRow) {
    throw new Error('包含空行');
  }
  return {
    success: true,
    message: `已成功导入 ${data.length} 行数据，系统正在刷新列表。`
  };
}
