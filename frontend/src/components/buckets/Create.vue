<template>
  <a-form
    :form="form"
    @submit="handleSubmit"
    class='create-form'
  >
    <a-form-item>
      <a-input
        v-decorator="[
          'name',
          { rules: [{ required: true, message: 'Please input the bucket name!' }] }
        ]"
        placeholder="Name"
      />
    </a-form-item>
    <a-form-item>
      <a-select
        v-decorator="[
          'bucket_type',
          {initialValue: 'Amazon S3'},
          {rules: [{ required: true, message: 'Please select the bucket type' }]}
        ]" 
        @change="handleTypeChange"
      >
        <a-select-option value="Amazon S3">Amazon S3</a-select-option>
        <a-select-option value="Google Storage">Google Storage</a-select-option>
      </a-select>
    </a-form-item>
    <div v-if="googleStorage == false">
      <a-form-item>
        <a-input
          v-decorator="[
            'aws_access_key',
            { rules: [{ required: true, message: 'Please input the AWS Access key!' }] }
          ]"
          placeholder="AWS Access Key"
        />
      </a-form-item>
      <a-form-item>
        <a-input
          v-decorator="[
            'aws_secret_key',
            { rules: [{ required: true, message: 'Please input the AWS Secret Key!' }] }
          ]"
          placeholder="AWS Secret Key"
        />
      </a-form-item>
    </div>
    <div v-else>
      <a-form-item>
        <a-input
          v-decorator="[
            'project_id',
            { rules: [{ required: true, message: 'Please input project id!' }] }
          ]"
          placeholder="Project ID"
        />
      </a-form-item>
      <a-form-item>
        <a-textarea 
          placeholder="Google json credentials" 
          :autosize="{ minRows: 10, maxRows: 100 }"
          v-decorator="[
            'credentials',
            { rules: [{ required: true, message: 'Please input the Google credentials!' }] }
          ]" 
        />
      </a-form-item>
    </div>
    <a-form-item class='btn-submit'>
      <a-button type="primary" html-type="submit">Submit</a-button>
    </a-form-item>
  </a-form>
</template>
<script>
import axios from 'axios'
export default {
  data () {
    return {
      googleStorage: false,
      form: this.$form.createForm(this)
    }
  },
  methods: {
    handleSubmit (e) {
      e.preventDefault()
      console.log(this.form)
      this.form.validateFields((err, values) => {
        if (!err) {
          console.log('Received values of form: ', values)
          const path = `http://localhost:5000/api/buckets`
          axios.post(path, values)
          .then(response => {
            this.$router.push('/')
          })
          .catch(error => {
            console.log(error)
          })
        }
      })
    },
    handleTypeChange (value) {
      console.log(value)
      if (value === 'Google Storage') {
        this.googleStorage = true
      } else {
        this.googleStorage = false
      }
    }
  }
}
</script>
<style scoped>
.create-form {
  width: 70%;
}
.btn-submit {
  float: left;
}
</style>
