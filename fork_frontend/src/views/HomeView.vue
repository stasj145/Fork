<script setup lang="ts"></script>

<template>
  <div class="home-container">
    <main>
      <div class="content">
        <h2>Dashboard</h2>
        <p>You are successfully logged in!</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-container {
  min-width: 100%;
  background-color: #f5f5f5;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #333;
  margin: 0;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background-color: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #e45656;
}

main {
  padding: 2rem;
}

.content {
  max-width: 800px;
  min-width: 100%;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #333;
  margin-top: 0;
}

p {
  color: #666;
  font-size: 1.1rem;
}
</style>
