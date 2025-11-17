// Initialize MongoDB collections and indexes

db = db.getSiblingDB('video_ai');

// Create users collection
db.createCollection('users');
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 }, { unique: true });

// Create videos collection
db.createCollection('videos');
db.videos.createIndex({ user_id: 1 });
db.videos.createIndex({ status: 1 });
db.videos.createIndex({ created_at: -1 });

// Create jobs collection
db.createCollection('jobs');
db.jobs.createIndex({ video_id: 1 });
db.jobs.createIndex({ status: 1 });
db.jobs.createIndex({ created_at: -1 });

// Create recommendations collection
db.createCollection('recommendations');
db.recommendations.createIndex({ user_id: 1 });
db.recommendations.createIndex({ video_id: 1 });
db.recommendations.createIndex({ score: -1 });

// Create feedback collection
db.createCollection('feedback');
db.feedback.createIndex({ user_id: 1 });
db.feedback.createIndex({ video_id: 1 });
db.feedback.createIndex({ created_at: -1 });

print("MongoDB initialization completed");
