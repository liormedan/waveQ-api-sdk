import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

export async function GET(
    request: NextRequest,
    { params }: { params: { path: string[] } }
) {
    try {
        const filePath = path.join(process.cwd(), 'uploads', ...params.path);

        if (!existsSync(filePath)) {
            return new NextResponse('File not found', { status: 404 });
        }

        const file = await readFile(filePath);
        const ext = path.extname(filePath).toLowerCase();

        // Determine content type
        const contentTypes: Record<string, string> = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.flac': 'audio/flac',
            '.aac': 'audio/aac',
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm',
        };

        const contentType = contentTypes[ext] || 'application/octet-stream';

        return new Response(file, {
            headers: {
                'Content-Type': contentType,
                'Cache-Control': 'public, max-age=3600',
            },
        });
    } catch (error) {
        console.error('Error serving file:', error);
        return new NextResponse('Internal Server Error', { status: 500 });
    }
}
