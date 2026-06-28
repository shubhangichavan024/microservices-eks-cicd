# user-service/Dockerfile

# Start with a tiny Node.js image
FROM node:18-alpine

# Our working directory inside container       
WORKDIR /app  

# Copy package files first (layer caching)
COPY package*.json ./      

# Install dependencies
RUN npm install            

# Copy rest of source code
COPY . .                   

# Tell Docker this port is used
EXPOSE 3000                

# Command to start the app
CMD ["node", "server.js"] 
