A great project idea to learn system design while working with **real-time data from Reddit** is to build a **Real-Time Trending Topic System**. This system would track and display the most discussed topics (or subreddits) in real time, giving users insights into what’s trending across Reddit at any given moment.

### Core Components of the System:

1. **Reddit Data Stream**:
   - Use Reddit's **API** (or a Reddit stream API) to ingest real-time data, such as new posts, comments, upvotes, etc.
   - Capture data from specific subreddits, or even across all subreddits, focusing on new posts and comments that are gaining traction.

2. **Kafka for Data Ingestion**:
   - Set up **Apache Kafka** as a message queue to handle the high-throughput data stream coming from Reddit.
   - Each Reddit post/comment would be pushed into Kafka topics (for example, `reddit-posts`, `reddit-comments`).
   - Producers (your data ingestion components) would send new Reddit posts/comments to Kafka.
   - Kafka would decouple the data producer (Reddit stream) from the consumer (your system’s processing logic).

3. **NoSQL Database (e.g., MongoDB or DynamoDB)**:
   - Use a **NoSQL database** to store the Reddit post data.
     - **Posts**: Store the content of Reddit posts, metadata (author, timestamp, subreddit, etc.), and engagement metrics (upvotes, comments).
     - **Comments**: Store comments and their metadata.
     - **Trending Data**: Store aggregated data on trending topics (tags, subreddits, keywords).
   - NoSQL is ideal here due to the unstructured nature of Reddit data and the need to scale horizontally as the data volume grows.
   - Use **DynamoDB** for high throughput and low-latency writes if you're working on AWS, or **MongoDB** for a flexible schema if you're working locally or in another cloud environment.

4. **Real-Time Analytics and Aggregation**:
   - Set up a **consumer** that reads from the Kafka topic (e.g., `reddit-posts`, `reddit-comments`) and processes the data in real time.
   - This consumer could perform:
     - **Text analysis**: Extract trending keywords or hashtags.
     - **Engagement tracking**: Aggregate post and comment counts, upvotes, etc.
   - This processing could be done using a **stream processing framework** like **Apache Flink** or **Apache Spark**.

5. **Cache (Redis)**:
   - Use a **cache** (e.g., **Redis**) to store the most popular and trending topics in real time.
     - Keep track of trending keywords, posts, or subreddits in **Redis** for quick lookup.
     - **Expire old data**: Set TTL (time-to-live) for cached data to ensure freshness and avoid serving outdated results.
   - Caching allows fast retrieval of trending topics and reduces the load on the database when displaying real-time results to users.

6. **Frontend (Web or App)**:
   - Display the trending posts or subreddits in real time on a **dashboard**.
   - Use **WebSockets** to push updates to the frontend in real time as new posts/comments are ingested and processed.
   - **Visualization**: Show trending topics, charts, word clouds, etc., based on real-time data from the backend.

### High-Level Flow:
1. **Kafka Producers** (Reddit data stream):
   - Fetch new posts/comments from Reddit (using Reddit API or a streaming API).
   - Send this data to Kafka topics (`reddit-posts`, `reddit-comments`).

2. **Kafka Consumers** (Real-time processing):
   - Process incoming Reddit data in real time (using Kafka consumers).
   - Extract relevant metadata (e.g., subreddit, keywords, post engagement) and aggregate it.
   - Store aggregated data in a **NoSQL database** (e.g., MongoDB or DynamoDB).

3. **Cache (Redis)**:
   - Store popular and trending topics in Redis for fast access.
   - Cache the top trending keywords or subreddits, expiring older data after a set TTL.

4. **Frontend**:
   - Fetch and display the trending topics to users, continuously updating with the most recent data.
   - Use **WebSockets** or **server-sent events (SSE)** to push real-time updates to the frontend.

### Why This is a Good Learning Experience:
- **Kafka**: You’ll get hands-on experience with message queues and high-throughput data streaming.
- **NoSQL Database**: You’ll learn how to store and process unstructured data, handle large volumes of data, and work with scalable, distributed databases.
- **Caching**: You’ll implement an efficient caching layer (Redis) to improve read performance and decrease latency for real-time data access.
- **Real-Time Analytics**: You’ll gain experience in stream processing and real-time data aggregation.
- **Scalability**: You’ll learn how to design a system that can handle massive amounts of data and scale as more users and posts come in.

### Extensions/Enhancements:
- **Sentiment Analysis**: Implement sentiment analysis to track the overall sentiment (positive, negative, neutral) of the trending posts or comments.
- **User Notifications**: Allow users to subscribe to specific subreddits or topics and send them notifications when new posts related to their interests appear.
- **Trending Predictions**: Use machine learning to predict potential future trends based on historical data.

This system would simulate a real-world use case for handling high-throughput data, leveraging a combination of Kafka, NoSQL databases, and caching for efficiency and scalability.'

# Learnings
* Websockets
   - For this project I'm using FlaskIO, I first tried seperating the task of consuming messsages from the queue into a seperate task and then emitting them one by one by using 
      - ```python 
            from threads import Thread
            from FlaskIO import socketio
            for message in consumer:
               socketio.emit("new_message", message)
         ```
   - But when I moved this processing to a seperate thread it lost context for the connection to client and therefore didn't know which endpoint to use for the socket connection among other things.
   - Also a way to check what running on a part that may be causes 403 errors when trying to access that port. You would run lsof -i :5000 to see what's running. 

