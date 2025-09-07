FROM node:20-alpine

WORKDIR /app

# Copy only package files first to leverage Docker cache when installing
COPY package.json ./
RUN npm install

# Copy the rest of the source
COPY . .

EXPOSE 5173

# Default command starts Vite dev server on all interfaces
CMD ["npm", "run", "dev", "--", "--host"]