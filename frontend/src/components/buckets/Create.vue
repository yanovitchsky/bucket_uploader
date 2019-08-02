<template>
  <a-form
    :form="form"
    @submit="handleSubmit"
  >
    <a-form-item>
      <a-input
        v-decorator="[
          'Name',
          { rules: [{ required: true, message: 'Please input the bucket name!' }] }
        ]"
        placeholder="Name"
      />
    </a-form-item>
    <a-form-item>
      <a-select defaultValue="Amazon S3" @change="handleTypeChange">
        <a-select-option value="Amazon S3">Amazon S3</a-select-option>
        <a-select-option value="Google Storage">Google Storage</a-select-option>
      </a-select>
    </a-form-item>
    <div v-if="googleStorage == false">
      <a-form-item>
        <a-input
          v-decorator="[
            'AWS Access Key',
            { rules: [{ required: true, message: 'Please input the AWS Access key!' }] }
          ]"
          placeholder="AWS Access Key"
        />
      </a-form-item>
      <a-form-item>
        <a-input
          v-decorator="[
            'AWS Secret Key',
            { rules: [{ required: true, message: 'Please input the AWS Secret Key!' }] }
          ]"
          placeholder="AWS Secret Key"
        />
      </a-form-item>
    </div>
    <div v-else>
      <a-form-item>
        <a-textarea placeholder="Google json credentials" :autosize="{ minRows: 10, maxRows: 10 }" />
      </a-form-item>
    </div>
  </a-form>
</template>
<script>
export default {
  data () {
    return  {
      googleStorage: false
    }
  },
  methods: {
    handleTypeChange (value) {
      console.log(value)
      if (value == "Google Storage") {
        this.googleStorage = true
      }
      else {
        this.googleStorage = false
      }
    }
  }
}
</script>

