# --- 阶段 1: 联网构建 ---
    FROM node:18-alpine as build-stage
    WORKDIR /app
    
    # 1. 复制描述文件
    COPY package.json ./
    
    # 2. 【新增：关键步骤】设置淘宝/阿里镜像源，加速下载
    RUN npm config set registry https://registry.npmmirror.com && \
        npm install
    
    # 3. 复制剩余源码并打包
    COPY . .
    RUN npm run build

# 第二阶段：运行（Production）
FROM nginx:stable-alpine AS production-stage
# 将编译好的静态文件复制到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html
# 复制你自定义的 Nginx 配置（处理路由跳转）
# COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]