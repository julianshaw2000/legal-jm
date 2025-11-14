/**
 * This is not a production server yet!
 * This is only a minimal backend to get started.
 */

import { Logger } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app/app.module';
import helmet from 'helmet';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { cors: false });

  const globalPrefix = 'api';
  app.setGlobalPrefix(globalPrefix);

  // Enable shutdown hooks for graceful Prisma disconnection
  app.enableShutdownHooks();

  // Security
  app.use(helmet());
  const origin = process.env.WEB_ORIGIN || 'http://localhost:4200';
  app.enableCors({ origin, credentials: true });

  // Swagger
  const config = new DocumentBuilder()
    .setTitle('Legal JM API')
    .setDescription('Jamaican Law Legal Advisor API')
    .setVersion('1.0.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup(`${globalPrefix}/docs`, app, document);

  const port = process.env.PORT ? Number(process.env.PORT) : 3000;
  await app.listen(port);
  Logger.log(`🚀 API: http://localhost:${port}/${globalPrefix}`);
  Logger.log(`📘 Swagger: http://localhost:${port}/${globalPrefix}/docs`);
}

bootstrap();
