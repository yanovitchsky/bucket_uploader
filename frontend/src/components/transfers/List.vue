<template>
  <div class="transfer-list">
    <div v-if="transfers.length > 0">
      <div class="add-bucket">
        <a-button type="primary" @click="newTransfer">Create a transfer</a-button>
      </div>
      <a-table 
        :columns="columns" 
        :dataSource="transfers" 
        :rowKey="record => record.id"/>
    </div>
    <div v-else>
      <div class="empty-bucket">No Transfer Yet</div>
      <div class="add-bucket">
        <a-button type="primary" @click="newTransfer">Create a transfer</a-button>
      </div>
    </div>
  </div>
</template>
<script>
import axios from 'axios'
const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    width: 150
  },
  {
    title: 'Source',
    dataIndex: 'source',
    width: 150
  },
  {
    title: 'Sink',
    dataIndex: 'sink',
    width: 150
  },
  {
    title: 'Success',
    dataIndex: 'success',
    width: 150
  },
  {
    title: 'Creation',
    dataIndex: 'createdAt',
    width: 150
  }
]
export default {
  data () {
    return {
      transfers: [],
      columns
    }
  },
  methods: {
    newTransfer () {
      this.$router.push('/transfers/new')
    },
    getTransfers () {
      const path = `http://localhost:5000/api/transfers`
      axios.get(path)
      .then(response => {
        this.transfers = response.data.transfers
      })
      .catch(error => {
        console.log(error)
      })
    },
    async getStatus (id) {
      try {
        const path = `http://localhost:5000/api/transfers/${id}/status`
        reponse = await axios.get(path)
        console.log(response.data);
      } catch (error) {
        console.log(error);
      }
    }
  },
  mounted () {
    this.getTransfers()
  },
  created () {
    // setInterval(() => {
    //   this.transfers.forEach(element => {
    //     this.getStatus(element.id)
    //   })
    // }, 10000)
  }
}
</script>
<style scoped>
.add-bucket {
  padding-bottom: 20px;
}
</style>