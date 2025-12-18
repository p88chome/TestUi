<template>
  <div class="card p-3">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-xl font-bold m-0 text-900">User Management</h2>
      <Button label="New User" icon="pi pi-plus" size="small" @click="openNewUser" />
    </div>

    <!-- User List -->
    <DataTable :value="users" :loading="loading" class="p-datatable-sm" tableStyle="min-width: 50rem">
        <Column field="id" header="ID" style="width: 10%"></Column>
        <Column field="email" header="Email"></Column>
        <Column field="full_name" header="Full Name"></Column>
        <Column field="is_active" header="Active">
            <template #body="slotProps">
                <Tag :value="slotProps.data.is_active ? 'Yes' : 'No'" :severity="slotProps.data.is_active ? 'success' : 'danger'" />
            </template>
        </Column>
        <Column field="is_superuser" header="Admin">
            <template #body="slotProps">
                <Tag :value="slotProps.data.is_superuser ? 'Yes' : 'No'" :severity="slotProps.data.is_superuser ? 'warning' : 'info'" />
            </template>
        </Column>
    </DataTable>

    <!-- Create User Dialog -->
     <Dialog v-model:visible="userDialog" :style="{ width: '450px' }" header="User Details" :modal="true" class="p-fluid">
        <div class="field">
            <label for="email" class="font-bold">Email</label>
            <InputText id="email" v-model.trim="user.email" required="true" autofocus :class="{ 'p-invalid': submitted && !user.email }" />
            <small class="p-error" v-if="submitted && !user.email">Email is required.</small>
        </div>
        
        <div class="field">
            <label for="password" class="font-bold">Password</label>
            <Password id="password" v-model="user.password" :feedback="false" toggleMask required="true" :class="{ 'p-invalid': submitted && !user.password }" />
             <small class="p-error" v-if="submitted && !user.password">Password is required.</small>
        </div>

        <div class="field">
            <label for="fullName" class="font-bold">Full Name</label>
             <InputText id="fullName" v-model.trim="user.full_name" />
        </div>

        <div class="field-checkbox">
             <Checkbox id="isSuperuser" v-model="user.is_superuser" :binary="true" />
             <label for="isSuperuser" class="ml-2">Is Admin?</label>
        </div>

        <template #footer>
            <Button label="Cancel" icon="pi pi-times" text @click="hideDialog" />
            <Button label="Save" icon="pi pi-check" text @click="saveUser" />
        </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getUsers, createUser, type User, type UserCreate } from '../api/users';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Checkbox from 'primevue/checkbox';

// If toast is used in App, need to ensure Toast component is globally registered or imported
// Here passing silent true for error as basic MVP.

const users = ref<User[]>([]);
const userDialog = ref(false);
const loading = ref(false);
const submitted = ref(false);

const user = ref<UserCreate>({
    email: '',
    password: '',
    full_name: '',
    is_superuser: false
});

onMounted(() => {
    loadUsers();
});

const loadUsers = async () => {
    loading.value = true;
    try {
        users.value = await getUsers();
    } catch (error) {
        console.error('Failed to load users', error);
    } finally {
        loading.value = false;
    }
};

const openNewUser = () => {
    user.value = { email: '', password: '', full_name: '', is_superuser: false }; 
    submitted.value = false;
    userDialog.value = true;
};

const hideDialog = () => {
    userDialog.value = false;
    submitted.value = false;
};

const saveUser = async () => {
    submitted.value = true;
    if (user.value.email.trim() && user.value.password) {
        try {
            await createUser(user.value);
            userDialog.value = false;
            // Refresh list
            loadUsers(); 
        } catch (error) {
            console.error('Failed to create user', error);
            alert('Failed to create user. Email might be already taken.');
        }
    }
};
</script>
