import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

export async function GET(
    request: NextRequest,
    { params }: { params: { taskId: string } }
) {
    try {
        const { searchParams } = new URL(request.url);
        const fileType = searchParams.get('type') || 'audio';
        const taskId = params.taskId;

        // Determine file path based on type
        let filePath: string;
        let contentType: string;
        let filename: string;

        switch (fileType) {
            case 'audio':
                filePath = path.join(process.cwd(), 'uploads', 'processed', `${taskId}.wav`);
                contentType = 'audio/wav';
                filename = `${taskId}_processed.wav`;
                break;

            case 'transcript':
                filePath = path.join(process.cwd(), 'uploads', 'processed', `${taskId}_transcript.txt`);
                contentType = 'text/plain';
                filename = `${taskId}_transcript.txt`;
                break;

            case 'vocals':
            case 'drums':
            case 'bass':
            case 'other':
                filePath = path.join(process.cwd(), 'uploads', 'processed', taskId, `${fileType}.wav`);
                contentType = 'audio/wav';
                filename = `${taskId}_${fileType}.wav`;
                break;

            default:
                return new NextResponse('Invalid file type', { status: 400 });
        }

        // Check if file exists
        if (!existsSync(filePath)) {
            return new NextResponse('File not found', { status: 404 });
        }

        // Read and return file
        const file = await readFile(filePath);

        return new Response(file, {
            headers: {
                'Content-Type': contentType,
                'Content-Disposition': `attachment; filename="${filename}"`,
                'Cache-Control': 'private, max-age=3600',
            },
        });
    } catch (error) {
        console.error('Download error:', error);
        return new NextResponse('Internal Server Error', { status: 500 });
    }
}
