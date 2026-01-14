<template>
  <nav class="navbar-root">
    <div class="nav-items">
      <div class="nav-branding">
        <RouterLink class="nav-brand" to="/home" @click="collapseNavbarExpansion">Fork</RouterLink>
      </div>
      <div v-if="showNavigation" class="nav-menu-items" :class="{ expanded: isExpanded }">
        <router-link
          to="/today"
          class="nav-menu-link"
          :class="{ expanded: isExpanded }"
          @click="collapseNavbarExpansion"
        >
          <IconToday class="nav-icon" />
          <span class="nav-text" :class="{ expanded: isExpanded }">Today</span>
        </router-link>

        <router-link
          to="/log"
          class="nav-menu-link"
          :class="{ expanded: isExpanded }"
          @click="collapseNavbarExpansion"
        >
          <IconLogbook class="nav-icon" />
          <span class="nav-text" :class="{ expanded: isExpanded }">Log</span>
        </router-link>

        <router-link
          to="/food"
          class="nav-menu-link"
          :class="{ expanded: isExpanded }"
          @click="collapseNavbarExpansion"
        >
          <IconFood class="nav-icon" />
          <span class="nav-text" :class="{ expanded: isExpanded }">Food</span>
        </router-link>

        <router-link
          to="/activity"
          class="nav-menu-link"
          :class="{ expanded: isExpanded }"
          @click="collapseNavbarExpansion"
        >
          <IconActiveCalories class="nav-icon activity" />
          <span class="nav-text" :class="{ expanded: isExpanded }">Activity</span>
        </router-link>

        <router-link
          to="/profile"
          class="nav-menu-link"
          :class="{ expanded: isExpanded }"
          @click="collapseNavbarExpansion"
        >
          <IconProfile class="nav-icon" />
          <span class="nav-text" :class="{ expanded: isExpanded }">Profile</span>
        </router-link>
      </div>
      <div class="nav-toggle">
        <button class="nav-toggle-btn" @click="toggleNavbarExpansion">
          <svg
            v-if="!isExpanded"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 4 24 24"
            width="24"
            height="24"
          >
            <path fill="currentColor" d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 3 24 24" width="24" height="24">
            <path
              fill="currentColor"
              d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
            />
          </svg>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import IconToday from '@/components/icons/IconToday.vue'
import IconLogbook from '@/components/icons/IconLogbook.vue'
import IconFood from '@/components/icons/IconFood.vue'
import IconActiveCalories from './icons/IconActiveCalories.vue'
import IconProfile from '@/components/icons/IconProfile.vue'

const isExpanded = ref(false)
const route = useRoute()

const toggleNavbarExpansion = () => {
  isExpanded.value = !isExpanded.value
}

const collapseNavbarExpansion = () => {
  isExpanded.value = false
}

const showNavigation = computed(() => {
  if (route.name == 'login' || route.name == 'register') {
    return false
  }
  return true
})
</script>

<style scoped>
.navbar-root {
  display: flex;
  flex-direction: column;
  background-color: var(--color-accent-secondary);
  color: var(--color-text-primary);
  box-shadow: 0 0 5px var(--color-black);
  z-index: 1000;
  position: fixed;
  top: 0;
  left: 0;
  width: var(--navbar-width);
  min-height: var(--navbar-height);
}

.nav-items {
  display: flex;
  flex-direction: row;
  margin: 0.5rem;
  height: 2rem;
}

.nav-brand {
  font-size: 2rem;
  line-height: 1.5rem;
  font-weight: bold;
  color: var(--color-white);
  text-decoration: none;
}

.nav-menu-items {
  margin-left: 1rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
}

.nav-menu-link {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  height: var(--navbar-height);
  color: var(--color-text-primary);
  text-decoration: none;
  transition: background-color 0.3s;
}

.nav-menu-link:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.nav-menu-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.4);
}

.nav-icon {
  margin-right: 0.5rem;
  flex-shrink: 0;
}
.nav-icon.activity {
  height: 90%;
}

.nav-text {
  flex-grow: 1;
  color: var(--color-text-primary);
}

.nav-toggle {
  display: none;
}

.nav-toggle-btn {
  display: none;
}

/* Mobile */
@media (max-width: 480px) {
  .nav-text:not(.expanded) {
    display: none;
  }
  .nav-text.expanded {
    display: flex;
    margin-left: 0.5rem;
  }
  .nav-icon {
    margin-right: 0;
  }

  .nav-menu-items {
    margin-left: 0.5rem;
  }

  .nav-brand {
    line-height: 1.75rem;
    font-size: 1.5rem;
  }

  .nav-toggle {
    display: flex;
    padding: 0.5rem;
    margin-left: auto;
  }

  .nav-toggle-btn {
    display: flex;
    background: none;
    border: none;
    margin-left: auto;
    color: var(--color-text-secondary);
  }

  .nav-menu-items.expanded {
    position: absolute;
    top: var(--navbar-height);
    left: 0;
    flex-direction: column;
    align-items: start;
    background-color: var(--color-accent-secondary);
    width: var(--navbar-width);
    box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
    z-index: 1000;
    margin-left: 0;
  }

  .nav-menu-link.expanded {
    width: 100%;
  }
}
</style>
